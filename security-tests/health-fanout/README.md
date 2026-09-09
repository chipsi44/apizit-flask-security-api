# Health fan-out

## Objectif et abus représenté

Multiplier le travail derrière une seule invocation de santé. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /liveness` — 4 threads joints, 50 ms CPU par thread maximum.

```text
curl -X GET http://127.0.0.1:8080/liveness
```

## Observation attendue sur APIZIT

Comparer durée et mémoire ; une requête HTTP ne représente pas un seul travail applicatif.

## Protection à vérifier et réaction idéale

Enveloppe de calcul et métrologie par invocation. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
