# APIZIT flask — API adversariale bornée

Lancer une API de test locale et observer des comportements adversariaux contrôlés.
Fixture de sécurité pour une future campagne APIZIT **dev** ; aucun lancement AWS
n'est effectué par le dépôt ou sa CI. Ce projet est autonome et ne dépend pas du checkout APIZIT.

## Démarrage local

```text
python -m venv .venv
# Activer .venv selon votre shell, puis :
python -m pip install -r requirements-dev.txt
python -m flask --app app run --host 127.0.0.1 --port 8080
```

Dans un second terminal : `curl http://127.0.0.1:8080/health`.
Lire les scénarios avant leurs appels. Utiliser des données synthétiques et un seul
processus, sans reloader. Redémarrer uniquement pour une nouvelle série contrôlée.

## Bornes et interprétation

Les limites sont celles de cette fixture, **pas des limites commerciales APIZIT**.
100 admissions par processus ; Flask/FastAPI limitent aussi à 2 requêtes actives.
Le compteur n'est pas global entre instances et ne rend pas un déploiement public sûr
face à un trafic illimité. La future campagne doit borner appels, durée et nombre d'instances.
Une limite applicative atteinte ne prouve pas qu'APIZIT applique la même protection.
Les probes ci-dessous sont volontairement modestes : elles vérifient des mécanismes,
sans chercher à atteindre les quotas cloud ou provoquer un DoS.

Les neuf références Light/Heavy/private conservent leur contrat et leur health check immédiat.
Cette extension security possède son propre contrat de 18 routes.

## Scénarios

| Test | Endpoint | Risque | Borne |
| --- | --- | --- | --- |
| [Health CPU](security-tests/health/README.md) | `GET /health` | MEDIUM | 50 ms et 100 000 itérations maximum |
| [Health mémoire](security-tests/health-memory/README.md) | `GET /healthz` | MEDIUM | 8 MiB touchés puis libérés |
| [Health instable](security-tests/health-flap/README.md) | `GET /status` | LOW | Alternance 200/500, compteur partagé avec /ready |
| [Health progressif](security-tests/health-progressive/README.md) | `GET /ready` | LOW | 10 ms supplémentaires par compteur, plafond 200 ms |
| [Health lent](security-tests/health-slow/README.md) | `GET /readiness` | LOW | Sommeil fixe de 200 ms |
| [Health fan-out](security-tests/health-fanout/README.md) | `GET /liveness` | MEDIUM | 4 threads joints, 50 ms CPU par thread maximum |
| [Calcul CPU](security-tests/cpu/README.md) | `GET /cpu` | MEDIUM | 250 ms et 100 000 itérations maximum |
| [Allocation mémoire](security-tests/memory/README.md) | `GET /memory` | MEDIUM | 8 MiB, pages touchées, aucune rétention |
| [Occupation longue](security-tests/slow/README.md) | `GET /slow` | LOW | Sommeil fixe de 2 s |
| [Thread après réponse](security-tests/background/README.md) | `POST /background` | MEDIUM | 1 thread daemon, 200 ms CPU maximum ; refus du chevauchement |
| [État global Flask](security-tests/state/README.md) | `GET /state` | LOW | Compteurs fixes et identifiant aléatoire par processus |
| [Découverte runtime](security-tests/environment/README.md) | `GET /environment` | LOW | 4 variables autorisées et validées ; hostname haché ; profondeur du cwd |
| [AWS identity](security-tests/aws/README.md) | `GET /aws` | MEDIUM | Désactivé par défaut ; 1 GetCallerIdentity ; timeouts connexion/lecture 1 s ; pas de retry |
| [Écriture temporaire](security-tests/filesystem/README.md) | `POST /filesystem` | MEDIUM | 1 fichier synthétique de 1 MiB, écrasé dans un répertoire temporaire privé |
| [Lecture source témoin](security-tests/source/README.md) | `GET /source` | LOW | Lecture du seul fichier public app/source_canary.py ; taille et hash uniquement |
| [Sous-processus bénin](security-tests/subprocess-probe/README.md) | `POST /subprocess` | MEDIUM | 1 enfant Python -I -S, sommeil 100 ms, timeout 2 s, environnement minimal |
| [Contention](security-tests/contention/README.md) | `POST /contention` | LOW | Attente de verrou 100 ms, section critique 50 ms |
| [Course déterministe](security-tests/race/README.md) | `POST /race` | LOW | 2 threads, barrière 500 ms, compteur local perdu |

## Vérification

```text
ruff check .
ruff format --check .
pytest -q
```

La CI Linux/Windows utilise des doubles pour AWS et HTTP sortant. Les tests
font réellement fonctionner les petites charges CPU/mémoire et les routes ; le
test Flask lance un enfant Python bénin. Aucun paiement, déploiement ou appel AWS.
Un scan local APIZIT détecte les routes ; ce résultat n'est pas une attestation de sécurité.

Le rapport global, les protections analysées et le protocole de campagne se trouvent
dans le dépôt plateforme : `docs/SECURITY_TEST_APIS.md`.
