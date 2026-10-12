from alembic import op
revision="0002"
down_revision="0001"
branch_labels=None
depends_on=None

def upgrade():
    from app.db.base import Base
    from app import models
    bind=op.get_bind()
    Base.metadata.create_all(bind=bind)
    tenant_tables=["patient_identities","model_registry","knowledge_documents","feature_flags","ai_feedback","evaluation_runs","security_events"]
    for table in tenant_tables:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE {table} FORCE ROW LEVEL SECURITY')
        op.execute(f"""CREATE POLICY {table}_tenant_isolation ON {table}
        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true),'')::uuid)
        WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true),'')::uuid)""")
    op.execute("""DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='psymind_app') THEN
        GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO psymind_app;
        GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO psymind_app;
      END IF;
    END $$;""")

def downgrade():
    for table in ["security_events","evaluation_runs","ai_feedback","feature_flags","knowledge_documents","model_registry","patient_identities"]:
        op.drop_table(table)
