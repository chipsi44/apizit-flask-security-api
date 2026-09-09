# Occupation longue

## Objectif et abus représenté

Occuper un emplacement actif après l'admission initiale. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /slow` — Sommeil fixe de 2 s.

```text
curl -X GET http://127.0.0.1:8080/slow
```

## Observation attendue sur APIZIT

Observer finalisation de durée et libération de capacité.

## Protection à vérifier et réaction idéale

Finalisation et réconciliation de capacité. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
