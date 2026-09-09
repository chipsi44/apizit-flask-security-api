# Contention

## Objectif et abus représenté

Bloquer un état global partagé par plusieurs requêtes. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /contention` — Attente de verrou 100 ms, section critique 50 ms.

```text
curl -X POST http://127.0.0.1:8080/contention
```

## Observation attendue sur APIZIT

Deux appels bornés peuvent produire succès ou conflit applicatif 409 ; observer le compteur.

## Protection à vérifier et réaction idéale

Isolation et distinction conflits applicatifs/capacité plateforme. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

