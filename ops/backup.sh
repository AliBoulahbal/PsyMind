#!/bin/sh
set -eu
: "${BACKUP_DIR:=/var/backups/psymind}"
mkdir -p "$BACKUP_DIR"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_OWNER" -d "$POSTGRES_DB" -Fc > "$BACKUP_DIR/db-$stamp.dump"
sha256sum "$BACKUP_DIR/db-$stamp.dump" > "$BACKUP_DIR/db-$stamp.dump.sha256"
echo "Created $BACKUP_DIR/db-$stamp.dump"
