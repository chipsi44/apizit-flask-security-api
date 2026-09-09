import subprocess
import time
from unittest.mock import Mock

import pytest

from app import app, probes, routes


@pytest.fixture(autouse=True)
def isolation(monkeypatch):
    monkeypatch.setattr(routes, "REQUESTS", 0)
    monkeypatch.setattr(
        probes, "STATE", {"counter": 0, "background_completed": 0, "health_calls": 0}
    )
    monkeypatch.delenv("ADVERSARIAL_ALLOW_STS", raising=False)
    import botocore.client

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Real AWS calls forbidden in tests")

    monkeypatch.setattr(botocore.client.BaseClient, "_make_api_call", forbidden)


@pytest.mark.parametrize("path", ["/health", "/healthz", "/cpu", "/memory", "/liveness"])
def test_compute_executes_and_is_bounded(path):
    started = time.monotonic()
    response = app.test_client().get(path)
    assert response.status_code == 200
    assert time.monotonic() - started < 3
    assert response.is_json


def test_health_failure_and_progression(monkeypatch):
    api = app.test_client()
    assert [api.get("/status").status_code for _ in range(4)] == [200, 500, 200, 500]
    sleeper = Mock()
    monkeypatch.setattr(routes.time, "sleep", sleeper)
    for _ in range(25):
        assert api.get("/ready").status_code == 200
    assert all(0 < call.args[0] <= 0.2 for call in sleeper.call_args_list)
    assert api.get("/readiness").json["delay_seconds"] == 0.2
    assert api.get("/slow").json["delay_seconds"] == 2
    sleeper.assert_called_with(2)


def test_environment_never_enumerates_or_returns_secrets(monkeypatch):
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "DO-NOT-RETURN")
    monkeypatch.setenv("CUSTOM_INNOCENT_NAME", "DO-NOT-RETURN")
    monkeypatch.setenv("AWS_REGION", "DO-NOT-RETURN")
    monkeypatch.setenv("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", "512")
    response = app.test_client().get("/environment")
    assert "DO-NOT-RETURN" not in response.text
    assert "AWS_SECRET_ACCESS_KEY" not in response.text
    assert response.json["environment"]["AWS_REGION"] == "[REDACTED]"
    assert response.json["environment"]["AWS_LAMBDA_FUNCTION_MEMORY_SIZE"] == "512"


def test_sts_disabled_by_default():
    assert app.test_client().get("/aws").status_code == 403


def test_sts_only_identity_with_no_provider_fallback(monkeypatch):
    import boto3

    monkeypatch.setenv("ADVERSARIAL_ALLOW_STS", "1")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    client = Mock()
    client.get_caller_identity.return_value = {
        "Account": "000000000000",
        "Arn": "arn:synthetic",
        "UserId": "fixture",
        "Credentials": "DO-NOT-RETURN",
        "ResponseMetadata": {"secret": "DO-NOT-RETURN"},
    }
    session = Mock()
    session.client.return_value = client
    constructor = Mock(return_value=session)
    monkeypatch.setattr(boto3, "Session", constructor)
    response = app.test_client().get("/aws")
    assert response.status_code == 200
    assert set(response.json) == {"status", "region", "Account", "Arn", "UserId"}
    assert "DO-NOT-RETURN" not in response.text
    providers = constructor.call_args.kwargs["botocore_session"].get_component(
        "credential_provider"
    )
    assert [provider.METHOD for provider in providers.providers] == ["env"]
    options = session.client.call_args.kwargs
    assert options["endpoint_url"] == "https://sts.eu-central-1.amazonaws.com"
    assert options["config"].retries["total_max_attempts"] == 1
    assert options["config"].proxies == {}
    client.get_caller_identity.assert_called_once_with()
    client.close.assert_called_once()


def test_sts_errors_are_not_exposed(monkeypatch):
    import boto3

    monkeypatch.setenv("ADVERSARIAL_ALLOW_STS", "1")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    monkeypatch.setattr(boto3, "Session", Mock(side_effect=RuntimeError("DO-NOT-RETURN")))
    response = app.test_client().get("/aws")
    assert response.status_code == 503
    assert "DO-NOT-RETURN" not in response.text
    monkeypatch.setenv("AWS_REGION", "attacker.invalid")
    assert app.test_client().get("/aws").status_code == 400


def test_filesystem_only_owned_marker_and_fixed_source(monkeypatch):
    monkeypatch.setattr(probes, "SCRATCH", None)
    api = app.test_client()
    try:
        first = api.post("/filesystem").json
        second = api.post("/filesystem?path=/etc/shadow").json
        assert first["previous_marker"] is False
        assert second["previous_marker"] is True
        assert first["instance"] == second["instance"]
        assert second["written_bytes"] == 1024 * 1024
        assert api.get("/source?path=/etc/shadow").json["canary_readable"] is True
    finally:
        if probes.SCRATCH:
            probes.SCRATCH.cleanup()


def test_one_real_benign_child_and_timeout_path(monkeypatch):
    assert app.test_client().post("/subprocess").json == {"returncode": 0, "marker": True}
    run = Mock(side_effect=subprocess.TimeoutExpired("synthetic", 2))
    monkeypatch.setattr(probes.subprocess, "run", run)
    assert app.test_client().post("/subprocess").json == {"status": "unavailable"}
    assert run.call_args.kwargs["timeout"] == 2
    assert run.call_args.kwargs["shell"] is False
    assert not any("AWS" in key for key in run.call_args.kwargs["env"])


def test_race_and_global_state():
    api = app.test_client()
    assert api.post("/race").json == {"expected": 2, "observed": 1, "simulated_shared_state": True}
    assert api.post("/contention").json["counter"] == 1
    assert api.get("/state").json["counter"] == 1
    with probes.LOCK:
        assert api.post("/contention").status_code == 409


def test_background_completes_and_rejects_overlap():
    api = app.test_client()
    with probes.BACKGROUND:
        assert api.post("/background").status_code == 429
    assert api.post("/background").status_code == 202
    assert probes.BACKGROUND.acquire(timeout=2)
    try:
        assert api.get("/state").json["background_completed"] == 1
    finally:
        probes.BACKGROUND.release()


def test_process_lifetime_budget_and_concurrency(monkeypatch):
    api = app.test_client()
    monkeypatch.setattr(routes, "REQUESTS", 99)
    assert api.get("/state").status_code == 200
    assert api.get("/health").status_code == 429
    assert api.get("/health").status_code == 429
    monkeypatch.setattr(routes, "REQUESTS", 0)
    with routes.SLOTS, routes.SLOTS:
        assert api.get("/cpu").status_code == 429
    assert api.get("/state").status_code == 200
