from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    
    # Build schema from ORM metadata for this reference release.
    from app.db.base import Base
    from app import models
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

    tenant_tables = [
        "users", "patients", "consultations", "patient_diagnoses", 
        "allergies", "prescriptions", "clinical_documents", 
        "clinical_chunks", "risk_predictions", "agent_runs", 
        "audit_logs", "ai_usage"
    ]
    
    for table in tenant_tables:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
        op.execute(f'''
        CREATE POLICY {table}_tenant_isolation ON {table}
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true),'')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true),'')::uuid)
        ''')
        
    op.execute("CREATE INDEX IF NOT EXISTS ix_chunks_embedding_hnsw ON clinical_chunks USING hnsw (embedding vector_cosine_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_chunks_fts ON clinical_chunks USING gin (to_tsvector('simple', content))")
    
    # Runtime role privileges. Role is provisioned by production DB init.
    op.execute("""
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='psymind_app') THEN
        GRANT USAGE ON SCHEMA public TO psymind_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO psymind_app;
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO psymind_app;
      END IF;
    END $$;
    """)
    
    # Append-only at application role level: trigger blocks mutation.
    op.execute('''
    CREATE OR REPLACE FUNCTION block_audit_mutation() RETURNS trigger AS $$
    BEGIN RAISE EXCEPTION 'audit_logs is append-only'; END; $$ LANGUAGE plpgsql;
    ''')

    op.execute('''
    CREATE TRIGGER audit_no_update BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION block_audit_mutation();
    ''')

def downgrade():
    from app.db.base import Base
    from app import models
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)