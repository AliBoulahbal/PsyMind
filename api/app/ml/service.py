from dataclasses import dataclass
@dataclass
class RiskResult:
    score:float
    level:str
    explanation:dict
    model_version:str

def development_risk(features:dict)->RiskResult:
    # NOT a clinical predictive model. Deterministic engineering stub for synthetic test data only.
    missing=max(0,min(1,float(features.get("missed_followups",0))/10))
    incidents=max(0,min(1,float(features.get("recent_incidents",0))/5))
    score=round(0.45*missing+0.55*incidents,4)
    level="high" if score>=.7 else "medium" if score>=.35 else "low"
    return RiskResult(score,level,{"missed_followups":missing,"recent_incidents":incidents},"dev-rule-v1")
