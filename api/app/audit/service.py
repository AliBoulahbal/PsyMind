import hashlib, json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog

async def audit(db: AsyncSession, tenant_id, actor_id, action, resource_type, resource_id=None, payload=None):
    q = await db.execute(select(AuditLog).where(AuditLog.tenant_id==tenant_id).order_by(AuditLog.created_at.desc()).limit(1))
    prev = q.scalar_one_or_none()
    body = {
        "tenant_id": str(tenant_id), "actor_id": str(actor_id) if actor_id else None,
        "action": action, "resource_type": resource_type, "resource_id": str(resource_id) if resource_id else None,
        "payload": payload or {}, "prev_hash": prev.event_hash if prev else None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    row = AuditLog(**body, event_hash=digest)
    row.created_at = datetime.fromisoformat(body["created_at"])
    db.add(row)
