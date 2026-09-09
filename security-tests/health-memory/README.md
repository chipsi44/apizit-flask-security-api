# Health mémoire

## Objectif et abus représenté

Déplacer une allocation coûteuse dans un endpoint apparemment banal. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /healthz` — 8 MiB touchés puis libérés.

```text
curl -X GET http://127.0.0.1:8080/healthz
```

## Observation attendue sur APIZIT

Observer mémoire et latence des probes ; vérifier que le choix du chemin ne change pas les quotas.

## Protection à vérifier et réaction idéale

Mémoire du runtime et facturation des probes. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
