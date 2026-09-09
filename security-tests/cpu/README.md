# Calcul CPU

## Objectif et abus représenté

Consommer du calcul utile à l'attaquant dans une requête courte. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /cpu` — 250 ms et 100 000 itérations maximum.

```text
curl -X GET http://127.0.0.1:8080/cpu
```

## Observation attendue sur APIZIT

Mesurer durée Lambda et débit effectif ; le test ne vise pas la saturation.

## Protection à vérifier et réaction idéale

Timeout, mémoire et débit par compte. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

