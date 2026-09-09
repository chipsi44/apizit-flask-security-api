import hashlib
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INSTANCE = uuid.uuid4().hex
LOCK = threading.Lock()
BACKGROUND = threading.BoundedSemaphore(1)
STATE = {"counter": 0, "background_completed": 0, "health_calls": 0}
SCRATCH = None


def cpu(milliseconds=50):
    deadline = time.monotonic() + milliseconds / 1000
    iterations = 0
    for _ in range(100_000):
        if time.monotonic() >= deadline:
            break
        hashlib.sha256(b"synthetic-probe" * 64).digest()
        iterations += 1
    return {"iterations": iterations, "max_ms": milliseconds}


def memory():
    block = bytearray(8 * 1024 * 1024)
    for offset in range(0, len(block), 4096):
        block[offset] = 1
    return {"allocated_bytes": len(block), "touched_pages": len(block) // 4096}


def fanout():
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(cpu, [50] * 4))
    return {"workers": len(results), "results": results}


def background():
    if not BACKGROUND.acquire(blocking=False):
        return {"status": "busy"}, 429

    def work():
        try:
            cpu(200)
            with LOCK:
                STATE["background_completed"] += 1
        finally:
            BACKGROUND.release()

    worker = threading.Thread(target=work, daemon=True, name="bounded-probe")
    try:
        worker.start()
    except RuntimeError:
        BACKGROUND.release()
        return {"status": "unavailable"}, 503
    return {"status": "started", "instance": INSTANCE, "max_ms": 200}, 202


def environment():
    # Never enumerate os.environ, provider configuration, credential files or /proc.
    validators = {
        "AWS_REGION": r"(?:us|eu|ap|ca|sa|af|me|il|mx)-[a-z]+-\d",
        "AWS_DEFAULT_REGION": r"(?:us|eu|ap|ca|sa|af|me|il|mx)-[a-z]+-\d",
        "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": r"\d{2,5}",
        "AWS_EXECUTION_ENV": r"AWS_Lambda_python3\.12",
    }
    values = {}
    for key, pattern in validators.items():
        value = os.getenv(key)
        if value is not None:
            values[key] = value if re.fullmatch(pattern, value) else "[REDACTED]"
    result = {
        "instance": INSTANCE,
        "python": platform.python_version(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "cpu_count": os.cpu_count(),
        "hostname_fingerprint": hashlib.sha256(socket.gethostname().encode()).hexdigest()[:16],
        "cwd_depth": len(Path.cwd().parts),
        "uid": os.getuid() if hasattr(os, "getuid") else None,
        "environment": values,
    }
    if sys.platform != "win32":
        import resource

        result["limits"] = {
            "open_files": list(resource.getrlimit(resource.RLIMIT_NOFILE)),
            "address_space": list(resource.getrlimit(resource.RLIMIT_AS)),
        }
    return result


def identity():
    if os.getenv("ADVERSARIAL_ALLOW_STS") != "1":
        return {"status": "disabled", "operation": "GetCallerIdentity"}, 403
    # SDK signing may use the existing Lambda environment identity only. No profiles,
    # metadata, containers, AssumeRole, credential inspection, or credential output.
    import boto3
    import botocore.session
    from botocore.config import Config
    from botocore.credentials import CredentialResolver, EnvProvider

    region = os.getenv("AWS_REGION", "eu-central-1")
    if region not in {"eu-central-1", "eu-west-1", "us-east-1", "ap-southeast-1", "af-south-1"}:
        return {"status": "unsupported_region"}, 400
    try:
        session = botocore.session.Session()
        session.set_config_variable("config_file", os.devnull)
        session.set_config_variable("credentials_file", os.devnull)
        session.register_component("credential_provider", CredentialResolver([EnvProvider()]))
        client = boto3.Session(botocore_session=session).client(
            "sts",
            region_name=region,
            endpoint_url=f"https://sts.{region}.amazonaws.com",
            config=Config(
                connect_timeout=1,
                read_timeout=1,
                retries={"total_max_attempts": 1},
                proxies={},
            ),
        )
        try:
            result = client.get_caller_identity()
        finally:
            client.close()
        return {
            "status": "observed",
            "region": region,
            **{key: result[key] for key in ("Account", "Arn", "UserId")},
        }, 200
    except Exception:
        # SDK error messages can contain request details. Do not return or log them.
        return {"status": "unavailable", "operation": "GetCallerIdentity"}, 503


def filesystem():
    global SCRATCH
    with LOCK:
        if SCRATCH is None:
            SCRATCH = tempfile.TemporaryDirectory(prefix="apizit-adversarial-")
        root = Path(SCRATCH.name)
        marker = root / "synthetic.bin"
        existed = marker.exists()
        # A single owned file, fixed name, no caller-supplied paths, no accumulation.
        with marker.open("wb") as handle:
            handle.write(b"x" * (1024 * 1024))
        return {
            "instance": INSTANCE,
            "previous_marker": existed,
            "written_bytes": marker.stat().st_size,
            "tmp_exists": Path("/tmp").is_dir(),
            "cwd_exists": Path.cwd().is_dir(),
        }


def source_canary():
    # This exact fixture-owned file is the only source content ever read.
    source = Path(__file__).with_name("source_canary.py").read_bytes()
    return {
        "canary_readable": True,
        "bytes": len(source),
        "sha256": hashlib.sha256(source).hexdigest(),
    }


def child():
    try:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", "import time; time.sleep(0.1); print('probe-ok')"],
            shell=False,
            timeout=2,
            capture_output=True,
            text=True,
            env={key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR") if key in os.environ},
        )
        return {"returncode": result.returncode, "marker": result.stdout.strip() == "probe-ok"}
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "unavailable"}


def contention():
    acquired = LOCK.acquire(timeout=0.1)
    if not acquired:
        return {"status": "contended"}, 409
    try:
        time.sleep(0.05)
        STATE["counter"] += 1
        return {"instance": INSTANCE, "counter": STATE["counter"]}, 200
    finally:
        LOCK.release()


def race():
    local = {"counter": 0}
    barrier = threading.Barrier(2, timeout=0.5)

    def increment():
        value = local["counter"]
        barrier.wait()
        local["counter"] = value + 1

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            tasks = [pool.submit(increment) for _ in range(2)]
            for task in tasks:
                task.result(timeout=1)
        return {"expected": 2, "observed": local["counter"], "simulated_shared_state": True}
    except threading.BrokenBarrierError:
        return {"status": "unavailable"}
