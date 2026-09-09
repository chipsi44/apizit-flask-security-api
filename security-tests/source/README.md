# Lecture source témoin

## Objectif et abus représenté

Vérifier que le code embarqué reste lisible depuis le runtime. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /source` — Lecture du seul fichier public app/source_canary.py ; taille et hash uniquement.

```text
curl -X GET http://127.0.0.1:8080/source
```

## Observation attendue sur APIZIT

Observer le témoin ; aucune lecture générale de l'application, des fichiers système ou des secrets.

## Protection à vérifier et réaction idéale

Ne pas placer de secrets dans le code embarqué ; isolation du filesystem. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
