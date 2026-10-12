#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then echo "usage: $0 /path/to/db.dump"; exit 2; fi
dump="$1"
echo "DANGER: restore overwrites database state. Use a maintenance window."
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db \
  pg_restore --clean --if-exists -U "$POSTGRES_OWNER" -d "$POSTGRES_DB" < "$dump"
