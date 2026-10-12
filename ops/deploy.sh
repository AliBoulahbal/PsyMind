#!/bin/sh
set -eu
test -f .env.production || { echo ".env.production missing"; exit 1; }
docker compose --env-file .env.production -f docker-compose.prod.yml config >/dev/null
docker compose --env-file .env.production -f docker-compose.prod.yml build --pull
docker compose --env-file .env.production -f docker-compose.prod.yml up -d db redis minio
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrate
docker compose --env-file .env.production -f docker-compose.prod.yml up -d api web nginx
docker compose --env-file .env.production -f docker-compose.prod.yml ps
