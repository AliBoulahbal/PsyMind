#!/bin/sh
set -eu

# Run after creating .env.production from the template. This is a provisioning
# step; runtime inference remains on the customer's server.
if [ ! -f .env.production ]; then
  echo "Missing .env.production; copy the template and configure unique secrets first." >&2
  exit 1
fi
OLLAMA_MODEL=$(sed -n 's/^OLLAMA_MODEL=//p' .env.production | tail -n 1)
OLLAMA_MODEL=${OLLAMA_MODEL:-gemma3:4b}
COMPOSE="docker compose --env-file .env.production -f docker-compose.prod.yml"
$COMPOSE up -d ollama
# The Ollama model is downloaded to the dedicated customer's local volume.
docker compose --env-file .env.production -f docker-compose.prod.yml exec ollama ollama pull "$OLLAMA_MODEL"
# Preload the multilingual embedding model into a persistent local cache volume.
$COMPOSE run --rm --no-deps --entrypoint python api -c \
  "from sentence_transformers import SentenceTransformer; import os; m=SentenceTransformer(os.environ.get('EMBEDDING_MODEL','sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')); v=m.encode(['PsyMind modèle local'], normalize_embeddings=True); assert len(v[0]) == 384, f'Expected 384 dimensions, got {len(v[0])}'; print('Local embedding model ready; dimensions=384')"

echo "Local models are preloaded. Verify both models work, then restrict outbound network access at the host firewall."
