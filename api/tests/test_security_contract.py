def test_tenant_not_accepted_in_patient_schema():
    from app.schemas import PatientIn
    assert "tenant_id" not in PatientIn.model_fields
    assert "center_id" not in PatientIn.model_fields

def test_prescription_has_no_tenant_input():
    from app.schemas import PrescriptionIn
    assert "tenant_id" not in PrescriptionIn.model_fields

def test_dev_risk_is_labeled_development():
    from app.ml.service import development_risk
    r=development_risk({"missed_followups":2,"recent_incidents":1})
    assert r.model_version.startswith("dev-")
    assert 0 <= r.score <= 1
