# Découverte runtime

## Objectif et abus représenté

Identifier le runtime, sa mémoire configurée et ses limites sans secrets. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /environment` — 4 variables autorisées et validées ; hostname haché ; profondeur du cwd.

```text
curl -X GET http://127.0.0.1:8080/environment
```

## Observation attendue sur APIZIT

Comparer identité de processus, OS, Python, limites POSIX et régions ; valeurs hors format masquées.

## Protection à vérifier et réaction idéale

Environnement minimal ; absence de configuration du control plane. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
