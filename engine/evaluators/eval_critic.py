"""
CareerOS Evaluation Critic and Quality Gate Harness
===================================================
Inspects and scores draft JD evaluations against strict quality criteria:
1. 4-Pillar completeness with numerical scores and concrete evidence.
2. Distinct separation of hard dealbreakers vs compensable gaps.
3. Negative constraint fidelity (no false GO when dealbreaker exists).
4. Unambiguous strategic verdict (GO / CONDITIONAL GO / NO-GO).
5. Grounded pitch citing candidate's verified metrics (7 squads, SDD, EU AI Act, Alignify).
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Optional
from engine.profiles.models import CandidateProfile
from engine.profiles.manager import ProfileManager

@dataclass
class QualityGateResult:
    is_valid: bool
    quality_score: float  # 0 to 100
    passed_gates: List[str] = field(default_factory=list)
    failed_gates: List[str] = field(default_factory=list)
    critique: str = ""
    suggested_improvements: List[str] = field(default_factory=list)

def evaluate_draft_analysis(text: str, profile: Optional[CandidateProfile] = None) -> QualityGateResult:
    """Evaluates a draft JD analysis against CareerOS 5 quality gates."""
    cand_profile = profile or ProfileManager.load_profile()

    passed = []
    failed = []
    critiques = []
    improvements = []
    total_score = 0.0

    lower_text = text.lower()

    # Gate 1: 4-Pillar Completeness & Evidence (Weight: 25 pts)
    # Check if the text contains 4 distinct evaluation dimensions with numerical scores
    has_numerical = bool(re.search(r"\d+\s*(/|out of)\s*\d+", text)) or bool(re.search(r"\d+/100", text))
    
    # Generic pillar check (either domain-specific or universal pillars)
    p1 = "change management" in lower_text or "adoption" in lower_text or "culture" in lower_text or "architecture" in lower_text
    p2 = "agentic" in lower_text or "automation" in lower_text or "devops" in lower_text or "cloud" in lower_text or "infrastructure" in lower_text
    p3 = "scaled agile" in lower_text or "delivery" in lower_text or "sre" in lower_text or "execution" in lower_text or "reliability" in lower_text
    p4 = "executive" in lower_text or "commercial" in lower_text or "alignment" in lower_text or "leadership" in lower_text or "business" in lower_text

    if p1 and p2 and p3 and p4 and has_numerical:
        passed.append("Gate 1: All 4 pillars scored with numerical evidence")
        total_score += 25.0
    else:
        msg = "Missing numerical pillar scoring or pillar breakdown"
        failed.append(f"Gate 1: {msg}")
        critiques.append(msg)
        improvements.append("Explicitly score all 4 pillars with numerical breakdown and evidence citations.")

    # Gate 2: Dealbreakers vs Compensable Gaps (Weight: 20 pts)
    has_dealbreaker_section = any(w in lower_text for w in ["dealbreaker", "blocker", "hard constraint", "mandatory constraint"])
    has_gap_section = any(w in lower_text for w in ["gap", "compensable", "negotiable", "mitigation"])

    if has_dealbreaker_section and has_gap_section:
        passed.append("Gate 2: Clear separation of hard dealbreakers vs compensable gaps")
        total_score += 20.0
    else:
        failed.append("Gate 2: Insufficient distinction between hard dealbreakers and compensable gaps")
        critiques.append("Did not clearly separate non-negotiable dealbreakers from addressable gaps.")
        improvements.append("Add explicit breakdown separating hard dealbreakers (location/language) from compensable gaps (keywords/tooling).")

    # Gate 3: Negative Constraint Enforcement (Weight: 20 pts)
    # Dynamically check candidate's blocker languages and unacceptable commutes
    unmet_dealbreakers = []
    
    # Check blocker languages
    for lang in cand_profile.languages.blocker_languages:
        l_low = lang.lower()
        if l_low in lower_text and any(w in lower_text for w in ["fluent", "c1", "c2", "native", "mandatory", "required"]):
            unmet_dealbreakers.append(f"Mandatory {lang} requirement")

    # Check unacceptable commutes / locations
    for comm in cand_profile.mobility.unacceptable_commutes:
        c_low = comm.lower()
        if c_low in lower_text and any(w in lower_text for w in ["on-site", "onsite", "hybrid", "3 days", "2 days"]):
            unmet_dealbreakers.append(f"Unacceptable on-site commute: {comm}")

    has_unmet_dealbreaker = len(unmet_dealbreakers) > 0
    direct_go_verdict = bool(re.search(r"\b(decision|verdict)\s*:\s*(direct\s+go|go)\b", lower_text)) and not bool(re.search(r"conditional|pivot", lower_text))

    if has_unmet_dealbreaker and direct_go_verdict:
        failed.append(f"Gate 3 (CRITICAL): Negative constraint violated! Direct GO awarded despite unmet mandatory dealbreakers: {', '.join(unmet_dealbreakers)}")
        critiques.append(f"VIOLATION OF NEGATIVE CONSTRAINT: Direct GO awarded despite unmet mandatory dealbreakers: {', '.join(unmet_dealbreakers)}")
        improvements.append("Demote verdict from GO to CONDITIONAL GO or NO-GO / PIVOT due to unmet mandatory constraints.")
    else:
        passed.append("Gate 3: Negative constraint respected")
        total_score += 20.0

    # Gate 4: Clear Strategic Verdict (Weight: 15 pts)
    has_verdict = any(v in lower_text for v in ["go", "conditional go", "no-go", "pivot", "verdict", "decision"])
    if has_verdict:
        passed.append("Gate 4: Explicit strategic verdict provided")
        total_score += 15.0
    else:
        failed.append("Gate 4: Ambiguous strategic verdict")
        critiques.append("No clear GO / CONDITIONAL GO / NO-GO verdict identified.")
        improvements.append("Clearly state the final strategic verdict: GO, CONDITIONAL GO, or NO-GO / PIVOT.")

    # Gate 5: Grounded Pitch with Verified Metrics (Weight: 20 pts)
    has_pitch = any(w in lower_text for w in ["pitch", "subject:", "outreach", "cover letter", "proposal"])
    grounded_metrics = []

    # Check against candidate's declared proof metrics dynamically
    for pm in cand_profile.proof_metrics:
        matched = False
        for kw in pm.keywords:
            if kw.lower() in lower_text:
                matched = True
                break
        if matched:
            grounded_metrics.append(f"{pm.category} ({pm.label})")

    # Generic numerical metric detection if custom proof metrics not explicitly matched
    if not grounded_metrics:
        generic_nums = re.findall(r"\b\d+[\d,\.]*\s*(?:%|squads|engineers|clusters|days|months|years|k|m|eur|usd)\b", lower_text)
        if len(generic_nums) >= 2:
            grounded_metrics.append(f"Grounded Quantitative Metrics ({', '.join(generic_nums[:3])})")

    if has_pitch and len(grounded_metrics) >= 2:
        passed.append(f"Gate 5: Grounded pitch citing verified metrics ({', '.join(grounded_metrics)})")
        total_score += 20.0
    elif has_pitch:
        passed.append("Gate 5: Pitch present but weak on verified candidate metrics")
        total_score += 10.0
        improvements.append(f"Infuse the pitch with concrete candidate proof points from CV: {', '.join([pm.label for pm in cand_profile.proof_metrics])}")
    else:
        failed.append("Gate 5: Missing targeted outreach pitch")
        critiques.append("No actionable outreach pitch or counter-proposal drafted.")
        improvements.append("Include an executive outreach pitch tailored to the target recruiter or hiring lead.")

    is_valid = (total_score >= 80.0) and (len(failed) == 0 or (len(failed) == 1 and "CRITICAL" not in failed[0]))

    return QualityGateResult(
        is_valid=is_valid,
        quality_score=total_score,
        passed_gates=passed,
        failed_gates=failed,
        critique="; ".join(critiques) if critiques else "Evaluation satisfies all CareerOS quality gates.",
        suggested_improvements=improvements
    )
