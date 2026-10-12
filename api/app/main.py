from fastapi import FastAPI
from sqlalchemy import text
from app.db.session import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.auth.router import router as auth
from app.patients.router import router as patients
from app.clinical.router import router as clinical
from app.ai.router import router as ai
from app.agents.router import router as agents
from app.dashboard.router import router as dashboard
from app.documents.router import router as documents
from app.evaluation.router import router as evaluation
from app.identity.router import router as identity
from app.governance.router import router as governance

app=FastAPI(title=settings.app_name,version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
for r in (auth,patients,clinical,ai,agents,dashboard,documents,evaluation,identity,governance):
    app.include_router(r,prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status":"ok","version":"2.0.0"}

@app.get("/ready")
async def ready():
    # AI outage must not make the clinical record/CRM unavailable.
    async with SessionLocal() as db:
        await db.execute(text("SELECT 1"))
    return {"status":"ready","components":{"database":"ok"}}

@app.get("/ready/ai")
async def ready_ai():
    import httpx
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(3.0, connect=1.0)) as client:
            response = await client.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
        return {"status":"ready","provider":"ollama","model":settings.ollama_model}
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail={"status":"unavailable","provider":"ollama"})
