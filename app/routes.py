import threading
import time

from flask import request

from app import app, probes

SLOTS = threading.BoundedSemaphore(2)
BUDGET_LOCK = threading.Lock()
REQUESTS = 0


@app.before_request
def admit():
    global REQUESTS
    if not SLOTS.acquire(blocking=False):
        return {"status": "fixture_busy"}, 429
    request.environ["fixture_slot"] = True
    with BUDGET_LOCK:
        if REQUESTS >= 100:
            return {"status": "fixture_budget_exhausted", "restart_required": True}, 429
        REQUESTS += 1
    return None


@app.teardown_request
def release(_error):
    if request.environ.pop("fixture_slot", False):
        SLOTS.release()


@app.get("/health")
def health():
    """Health CPU. 50 ms et 100 000 itérations maximum."""
    return {"status": "ok", "probe": probes.cpu(50)}


@app.get("/healthz")
def health_memory():
    """Health mémoire. 8 MiB touchés puis libérés."""
    return {"status": "ok", "probe": probes.memory()}


@app.get("/status")
def health_flap():
    """Health instable. Alternance 200/500, compteur partagé avec /ready."""
    with probes.LOCK:
        probes.STATE["health_calls"] += 1
        code = 200 if probes.STATE["health_calls"] % 2 else 500
    return {"status": "ok" if code == 200 else "synthetic_failure"}, code


@app.get("/ready")
def health_progressive():
    """Health progressif. 10 ms supplémentaires par compteur, plafond 200 ms."""
    with probes.LOCK:
        probes.STATE["health_calls"] += 1
        delay = min(probes.STATE["health_calls"] * 0.01, 0.2)
    time.sleep(delay)
    return {"status": "ok", "delay_seconds": delay}


@app.get("/readiness")
def health_slow():
    """Health lent. Sommeil fixe de 200 ms."""
    time.sleep(0.2)
    return {"status": "ok", "delay_seconds": 0.2}


@app.get("/liveness")
def health_fanout():
    """Health fan-out. 4 threads joints, 50 ms CPU par thread maximum."""
    return {"status": "ok", "probe": probes.fanout()}


@app.get("/cpu")
def cpu():
    """Calcul CPU. 250 ms et 100 000 itérations maximum."""
    return probes.cpu(250)


@app.get("/memory")
def memory():
    """Allocation mémoire. 8 MiB, pages touchées, aucune rétention."""
    return probes.memory()


@app.get("/slow")
def slow():
    """Occupation longue. Sommeil fixe de 2 s."""
    time.sleep(2)
    return {"delay_seconds": 2}


@app.post("/background")
def background():
    """Thread après réponse. 1 thread daemon, 200 ms CPU maximum ; refus du chevauchement."""
    return probes.background()


@app.get("/state")
def state():
    """État global Flask. Compteurs fixes et identifiant aléatoire par processus."""
    with probes.LOCK:
        return {"instance": probes.INSTANCE, **probes.STATE}


@app.get("/environment")
def environment():
    """Découverte runtime. 4 variables autorisées et validées ; hostname haché ; profondeur du
    cwd.
    """
    return probes.environment()


@app.get("/aws")
def aws():
    """AWS identity. Désactivé par défaut ; 1 GetCallerIdentity ; timeouts connexion/lecture 1
    s ; pas de retry.
    """
    return probes.identity()


@app.post("/filesystem")
def filesystem():
    """Écriture temporaire. 1 fichier synthétique de 1 MiB, écrasé dans un répertoire
    temporaire privé.
    """
    return probes.filesystem()


@app.get("/source")
def source():
    """Lecture source témoin. Lecture du seul fichier public app/source_canary.py ; taille et
    hash uniquement.
    """
    return probes.source_canary()


@app.post("/subprocess")
def subprocess_probe():
    """Sous-processus bénin. 1 enfant Python -I -S, sommeil 100 ms, timeout 2 s, environnement
    minimal.
    """
    return probes.child()


@app.post("/contention")
def contention():
    """Contention. Attente de verrou 100 ms, section critique 50 ms."""
    return probes.contention()


@app.post("/race")
def race():
    """Course déterministe. 2 threads, barrière 500 ms, compteur local perdu."""
    return probes.race()
