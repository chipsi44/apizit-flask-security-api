# Écriture temporaire

## Objectif et abus représenté

Tester écriture, présence de /tmp et réutilisation d'un marqueur à chaud. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /filesystem` — 1 fichier synthétique de 1 MiB, écrasé dans un répertoire temporaire privé.

```text
curl -X POST http://127.0.0.1:8080/filesystem
```

## Observation attendue sur APIZIT

Appeler deux fois et comparer previous_marker et instance ; un nouveau processus doit être indépendant.

## Protection à vérifier et réaction idéale

Stockage éphémère et isolation des instances. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
