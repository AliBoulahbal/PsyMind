import httpx
from app.core.config import settings
async def export_event(payload:dict)->bool:
    if not settings.external_audit_url:return False
    headers={"Authorization":f"Bearer {settings.external_audit_token}"} if settings.external_audit_token else {}
    async with httpx.AsyncClient(timeout=5) as c:
        r=await c.post(settings.external_audit_url,json=payload,headers=headers)
        r.raise_for_status()
    return True
