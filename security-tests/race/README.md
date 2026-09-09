# Course déterministe

## Objectif et abus représenté

Démontrer une mise à jour perdue dans le code client. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /race` — 2 threads, barrière 500 ms, compteur local perdu.

```text
curl -X POST http://127.0.0.1:8080/race
```

## Observation attendue sur APIZIT

Observer expected=2 et observed=1 ; ne pas attribuer cette course applicative à DynamoDB/APIZIT.

## Protection à vérifier et réaction idéale

Isolation des clients, pas correction des bugs de leur code. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
