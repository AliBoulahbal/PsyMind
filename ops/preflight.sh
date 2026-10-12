#!/bin/sh
set -eu
echo "[1/7] environment"
test -f .env.production || { echo "FAIL .env.production missing"; exit 1; }
grep -q "ENVIRONMENT=production" .env.production || { echo "FAIL ENVIRONMENT"; exit 1; }
! grep -q "REPLACE_\\|CHANGE_ME" .env.production || { echo "FAIL placeholders remain"; exit 1; }
echo "[2/7] compose"
docker compose --env-file .env.production -f docker-compose.prod.yml config >/dev/null
echo "[3/7] python tests"
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm --no-deps api pytest -q
echo "[4/7] migrations"
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrate
echo "[5/7] local model provisioning"
sh ops/pull-local-models.sh
echo "[6/7] services"
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
sleep 8
curl -fsS http://127.0.0.1/healthz >/dev/null
echo "[7/7] status"
docker compose --env-file .env.production -f docker-compose.prod.yml ps
echo "PREFLIGHT PASS - verify local model readiness, apply Docker-aware egress restrictions, and run tenant-isolation, restore, E2E, clinical and legal reviews before real patient data."
