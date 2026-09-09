# Allocation mémoire

## Objectif et abus représenté

Faire monter la consommation mémoire sans grosse réponse HTTP. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /memory` — 8 MiB, pages touchées, aucune rétention.

```text
curl -X GET http://127.0.0.1:8080/memory
```

## Observation attendue sur APIZIT

Comparer mémoire maximale et récupération entre requêtes.

## Protection à vérifier et réaction idéale

Limites mémoire du runtime et isolation des APIs. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
