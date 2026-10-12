#!/bin/sh
set -eu
BASE="${BASE_URL:-https://localhost}"
echo "Health:"
curl -fkSs "$BASE/healthz"
echo
echo "Containers:"
docker compose --env-file .env.production -f docker-compose.prod.yml ps
echo "Recent API errors:"
docker compose --env-file .env.production -f docker-compose.prod.yml logs --since=10m api | tail -100
echo "POSTDEPLOY BASIC PASS if health is OK and no service is unhealthy."
