#!/bin/sh
python3 - <<'PY'
import secrets
for k in ["SECRET_KEY","POSTGRES_OWNER_PASSWORD","POSTGRES_APP_PASSWORD","REDIS_PASSWORD","MINIO_ACCESS_KEY","MINIO_SECRET_KEY"]:
    print(f"{k}={secrets.token_urlsafe(48)}")
PY
