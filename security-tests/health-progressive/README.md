# Health progressif

## Objectif et abus représenté

Dissimuler une dégradation qui apparaît après quelques invocations. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /ready` — 10 ms supplémentaires par compteur, plafond 200 ms.

```text
curl -X GET http://127.0.0.1:8080/ready
```

## Observation attendue sur APIZIT

Comparer latence à chaud et à froid ; le compteur est propre au processus.

## Protection à vérifier et réaction idéale

Timeout et décision de promotion. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **LOW**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

