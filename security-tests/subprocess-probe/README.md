# Sous-processus bénin

## Objectif et abus représenté

Exécuter du travail hors du thread de la route. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /subprocess` — 1 enfant Python -I -S, sommeil 100 ms, timeout 2 s, environnement minimal.

```text
curl -X POST http://127.0.0.1:8080/subprocess
```

## Observation attendue sur APIZIT

Observer marqueur fixe et sortie de l'enfant ; aucun shell ni commande fournie par le client.

## Protection à vérifier et réaction idéale

Enveloppe de processus et arrêt des enfants. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
