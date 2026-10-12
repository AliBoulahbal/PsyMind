from dataclasses import dataclass
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.session import get_db, set_tenant

bearer = HTTPBearer()

@dataclass
class Principal:
    user_id: UUID
    tenant_id: UUID
    role: str
    permissions: list[str]

async def current_principal(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db)
):
    try:
        p = decode_token(creds.credentials)
        if p.get("type") != "access":
            raise ValueError("wrong token type")
        principal = Principal(UUID(p["sub"]), UUID(p["tenant_id"]), p["role"], p.get("permissions", []))
        await set_tenant(db, principal.tenant_id)
        return principal
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

def require(permission: str):
    async def dep(p: Principal = Depends(current_principal)):
        if p.role != "chief_psychiatrist" and permission not in p.permissions:
            raise HTTPException(403, f"Missing permission: {permission}")
        return p
    return dep
