# PsyMind V3 — plan de finalisation pour l'Algérie

## Décisions de déploiement
- Cible fonctionnelle : cabinets, cliniques, centres médicaux et hôpitaux, avec activation progressive des modules réellement validés.
- Installation : instance dédiée par client (API, base PostgreSQL, Redis, stockage objet, modèle local et sauvegardes).
- IA : Ollama local uniquement en production. Aucune clé d'API LLM externe ne doit être renseignée.
- Embeddings : modèle Sentence Transformers local à 384 dimensions, compatible avec `vector(384)`. Le cache du modèle doit être préchargé et testé avant de couper l'accès réseau sortant.
- Environnement : ne jamais copier un `.env` réel dans l'archive de livraison.

## Changements apportés dans cette passe
1. Ajout d'une validation de configuration de production imposant Ollama, embeddings locaux, clé PII dédiée et `AI_FAIL_OPEN=false`.
2. Le gateway IA interdit le fallback mock en production.
3. L'endpoint IA retourne une erreur contrôlée `503 AI_UNAVAILABLE` si le modèle local ne répond pas ; le dossier clinique reste accessible.
4. Ajout d'un service Ollama interne dans les fichiers Compose. Son port n'est pas publié sur l'hôte en production.
5. L'image API de production installe les dépendances d'embedding local.
6. Ajout d'une route de disponibilité IA séparée : `/ready/ai`.
7. La création d'une allergie vérifie maintenant que le patient appartient au tenant authentifié.
8. Ajout de `.gitignore` et suppression du fichier `.env` réel de l'archive de livraison.

## Installation locale de modèle (à exécuter sur le serveur dédié)
1. Générer les secrets et renseigner `.env.production` à partir de `.env.production.example`.
2. Lancer PostgreSQL/Redis/MinIO/Ollama et télécharger le modèle local choisi via `ollama pull gemma3:4b` (ou le modèle approuvé après évaluation matérielle/clinique).
3. Précharger le modèle Sentence Transformers configuré dans `EMBEDDING_MODEL` dans le cache local. Vérifier qu'il produit exactement 384 dimensions.
4. Une fois les modèles présents, appliquer des règles de pare-feu compatibles Docker pour bloquer le trafic sortant non nécessaire (notamment depuis les conteneurs applicatifs), puis confirmer que les parcours IA continuent de fonctionner.
5. Ne pas considérer le téléchargement initial des modèles comme une preuve d'absence de trafic sortant : contrôler les journaux réseau et la configuration du serveur.

## Commandes de vérification
```bash
# Vérifier la syntaxe des configurations (sans démarrer les services)
docker compose config -q
docker compose --env-file .env.production -f docker-compose.prod.yml config -q

# Démarrage de production après configuration des secrets et TLS
sh ops/preflight.sh
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d

# Vérifier les composants
curl -fsS https://VOTRE-DOMAINE/health
curl -fsS https://VOTRE-DOMAINE/ready
curl -fsS https://VOTRE-DOMAINE/ready/ai

# Tests backend dans l'environnement de test
PYTHONPATH=api pytest api/tests -q
```

## Critères de mise en production
- [ ] Aucun secret réel dans Git, ZIP, journaux, images ou rapports.
- [ ] `LLM_PROVIDER=ollama`, `EMBEDDING_PROVIDER=sentence_transformers`, `AI_FAIL_OPEN=false`, `LLM_API_KEY` vide.
- [ ] Aucun port PostgreSQL, Redis, MinIO ou Ollama exposé publiquement.
- [ ] Le préflight télécharge/précharge les modèles avant l'activation des règles de restriction egress ; les mises à jour de modèles sont ensuite des opérations contrôlées.
- [ ] Modèles IA et embeddings préchargés localement ; test sans accès Internet réussi.
- [ ] Migrations exécutées sur PostgreSQL réel ; tests RLS tenant A/B positifs et négatifs.
- [ ] Tests d'accès direct inter-tenant, RBAC, révocation/expiration de sessions et upload malveillant.
- [ ] Sauvegarde chiffrée et restauration vérifiée sur une instance isolée.
- [ ] Build frontend, tests E2E navigateur, scan de dépendances et pentest.
- [ ] Monitoring, alertes, plan d'incident, mises à jour et retour arrière documentés.
- [ ] Validation clinique, confidentialité et conformité algérienne par les professionnels compétents.

## Limites de cette passe
Cette passe est un durcissement initial du dépôt, pas une certification ni une autorisation d'utilisation clinique. Les tests d'intégration PostgreSQL/RLS, la construction des images, les téléchargements de modèles, les parcours E2E, la restauration, le pentest et la validation juridique/clinique doivent encore être exécutés sur un serveur cible.
