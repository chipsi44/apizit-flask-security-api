# Health CPU

## Objectif et abus représenté

Faire exécuter du calcul par les appels automatiques de santé. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /health` — 50 ms et 100 000 itérations maximum.

```text
curl -X GET http://127.0.0.1:8080/health
```

## Observation attendue sur APIZIT

Comparer appels publics et smoke attesté : durée, invocation et débit de crédits.

## Protection à vérifier et réaction idéale

Attestation, anti-rejeu, admission et finalisation du coût. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
