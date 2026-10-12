import asyncio
from sqlalchemy import select
from app.db.session import SessionLocal, set_tenant
from app.models import Tenant,User,Disease,Medication
from app.core.security import hash_password

PERMS=["patient.read","patient.write","consultation.write","diagnosis.write","prescription.write",
       "catalog.manage","clinical.ai.query","agent.propose","approve.ai_action"]

async def main():
    async with SessionLocal() as db:
        tenant=(await db.execute(select(Tenant).where(Tenant.slug=="demo-center"))).scalar_one_or_none()
        if not tenant:
            tenant=Tenant(slug="demo-center",name="Synthetic Demo Center"); db.add(tenant); await db.flush()
            await set_tenant(db, tenant.id)
            db.add(User(tenant_id=tenant.id,email="admin@psymind.local",password_hash=hash_password("ChangeMe123!"),
                        full_name="Local Demo Admin",role="chief_psychiatrist",permissions=PERMS))
        else:
            await set_tenant(db, tenant.id)
        if not (await db.execute(select(Disease).limit(1))).scalar_one_or_none():
            db.add_all([
                Disease(code="LOCAL-DEP",name="Depressive disorder",description="Synthetic catalog entry"),
                Disease(code="LOCAL-ANX",name="Anxiety disorder",description="Synthetic catalog entry")
            ])
        if not (await db.execute(select(Medication).limit(1))).scalar_one_or_none():
            db.add_all([
                Medication(code="MED-001",generic_name="Synthetic Medication A",form="tablet",strength="10 mg"),
                Medication(code="MED-002",generic_name="Synthetic Medication B",form="capsule",strength="20 mg")
            ])
        await db.commit()

if __name__=="__main__": asyncio.run(main())
