import re
from dataclasses import dataclass

INJECTION_PATTERNS=[
 r"ignore (all|any|the) previous instructions",
 r"reveal (the )?(system|developer) prompt",
 r"act as (an? )?unrestricted",
 r"bypass (safety|policy|guardrails)",
]
HIGH_RISK_ACTIONS={"prescribe","change_medication","diagnose","discharge","involuntary_hold"}

@dataclass
class GuardResult:
    allowed:bool
    reasons:list[str]

def inspect_prompt(text:str)->GuardResult:
    reasons=[]
    low=text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern,low): reasons.append("prompt_injection_pattern")
    return GuardResult(not reasons,reasons)

def requires_human_approval(action:str)->bool:
    return action in HIGH_RISK_ACTIONS

def validate_grounding(answer: str, context: list[dict]) -> GuardResult:
    if not context:
        return GuardResult(False, ["no_retrieved_context"])
    cited = {int(value) for value in re.findall(r"\[SOURCE\s+(\d+)\]", answer, flags=re.IGNORECASE)}
    if not cited:
        return GuardResult(False, ["missing_source_citation"])
    available = min(len(context), 8)
    if any(value < 1 or value > available for value in cited):
        return GuardResult(False, ["invalid_source_citation"])
    return GuardResult(True, [])
