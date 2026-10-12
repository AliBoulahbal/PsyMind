from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db, set_tenant
from app.models import Tenant, User
from app.schemas import LoginIn, TokenOut
from app.core.security import verify_password, create_token
router=APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession=Depends(get_db)):
    tenant=(await db.execute(select(Tenant).where(Tenant.slug==data.tenant_slug, Tenant.active==True))).scalar_one_or_none()
    if not tenant: raise HTTPException(401,"Invalid credentials")
    await set_tenant(db, tenant.id)
    user=(await db.execute(select(User).where(User.tenant_id==tenant.id, User.email==data.email, User.active==True))).scalar_one_or_none()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,"Invalid credentials")
    kw=dict(user_id=user.id,tenant_id=tenant.id,role=user.role,permissions=user.permissions or [])
    return TokenOut(access_token=create_token(**kw),refresh_token=create_token(**kw,token_type="refresh"))
