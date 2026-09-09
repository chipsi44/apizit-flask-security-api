# Health instable

## Objectif et abus représenté

Perturber la décision de disponibilité et provoquer des relances. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /status` — Alternance 200/500, compteur partagé avec /ready.

```text
curl -X GET http://127.0.0.1:8080/status
```

## Observation attendue sur APIZIT

Observer état health et activation ; un 500 ne doit pas être annoncé comme sain.

## Protection à vérifier et réaction idéale

État de santé fidèle et retries bornés. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

