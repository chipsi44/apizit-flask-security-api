# Thread après réponse

## Objectif et abus représenté

Exécuter du travail après le retour de la route. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`POST /background` — 1 thread daemon, 200 ms CPU maximum ; refus du chevauchement.

```text
curl -X POST http://127.0.0.1:8080/background
```

## Observation attendue sur APIZIT

Lire /state après un appel ; comparer réponse client, fin Lambda et gel/reprise.

## Protection à vérifier et réaction idéale

Comptabilité de durée et cycle de vie du runtime. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.
