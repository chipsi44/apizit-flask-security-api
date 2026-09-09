# AWS identity

## Objectif et abus représenté

Apprendre l'identité IAM effective et le compte hébergeur. Ce scénario permet d'isoler ce comportement pendant une future
qualification, avec des données synthétiques.

## Comportement et endpoints

`GET /aws` — Désactivé par défaut ; 1 GetCallerIdentity ; timeouts connexion/lecture 1 s ; pas de retry.

```text
curl -X GET http://127.0.0.1:8080/aws
```

## Observation attendue sur APIZIT

Observer seulement Account, Arn, UserId et région ; un succès STS ne prouve aucun autre droit.

## Protection à vérifier et réaction idéale

Rôle client isolé du control plane et frontière de permissions. Le résultat doit rester borné et correctement attribué au
client, sans effet sur un autre workspace. Une observation locale ne démontre
pas cette propriété dans AWS.

## Risque et précautions

Niveau : **MEDIUM**, dans les bornes de la fixture. Lire le README racine,
utiliser un environnement jetable, commencer par un appel et ne pas utiliser
de load generator. Pas de production, de paiement, de données réelles, de
lecture de secrets ou de cible tierce. Le plafond par processus ne remplace
pas un budget global lors d'une campagne multi-instance.

Activation opérateur : définir `ADVERSARIAL_ALLOW_STS=1` uniquement dans un
runtime de test dev dédié lors de la future campagne. L'application laisse le SDK
signer avec l'identité déjà injectée dans l'environnement ; elle n'inspecte, ne
renvoie et ne sauvegarde aucun credential. Aucun provider de profil, fichier,
metadata, conteneur ou AssumeRole n'est activé. Les timeouts SDK sont des timeouts
socket et ne constituent pas une deadline globale de résolution DNS.
Les tests CI remplacent le SDK. Ne pas activer STS dans une session de développeur
munie de ses credentials habituels. Account/Arn/UserId sont non secrets mais ne
doivent pas être publiés dans les preuves de campagne sans nécessité.

