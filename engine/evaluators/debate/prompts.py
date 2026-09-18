"""
CareerOS Dual-Agent Debate Prompts
==================================
Dialectic prompt templates for the Skeptical Prosecutor and the Opportunity Advocate.
"""

from engine.profiles.models import CandidateProfile

def build_prosecutor_prompt(jd_text: str, profile: CandidateProfile) -> str:
    """Constructs an adversarial risk screening prompt to expose all flaws and dealbreakers."""
    
    proof_lines = [f"- {p.category} ({p.label}): {p.evidence}" for p in profile.proof_metrics]
    proof_str = "\n".join(proof_lines)
    
    blocker_langs = ", ".join(profile.languages.blocker_languages) or "None"
    unacc_commutes = ", ".join(profile.mobility.unacceptable_commutes) or "None"
    anti_roles = ", ".join(profile.scope.anti_roles) or "None"

    return f"""### ROLE: THE SKEPTICAL PROSECUTOR (CAREEROS RISK SCREENER & DEAL KILLER)
You are an uncompromising, skeptical senior talent auditor. Your SOLE objective is to PROTECT the candidate ({profile.full_name}) from bad deals, toxic mandates, boundary violations, and disguised low-value work.

### CANDIDATE BOUNDARIES & NEGATIVE CONSTRAINTS:
- Name: {profile.full_name}
- Base Location: {profile.mobility.base_location} | Remote Policy: {profile.mobility.remote_preference}
- Travel Tolerance: {profile.mobility.travel_tolerance}
- UNACCEPTABLE COMMUTES (FATAL DEALBREAKER): {unacc_commutes}
- NON-SPOKEN / BLOCKER LANGUAGES (FATAL DEALBREAKER): {blocker_langs}
- SPOKEN LANGUAGES: {", ".join(profile.languages.fluent_languages)}
- FORBIDDEN ANTI-ROLES (FATAL OR PIVOT): {anti_roles}
- COMMERCIAL BOUNDARIES: Target Freelance TJM {profile.commercials.freelance_tjm_eur} | Min Perm {profile.commercials.permanent_salary_eur}
- TARGET SENIORITY: {profile.scope.seniority} (Target Titles: {", ".join(profile.scope.primary_titles)})

### YOUR MISSION:
Inspect the following Job Description with extreme scrutiny. Do NOT be polite. Do NOT hallucinate fit.
1. Hunt down FATAL DEALBREAKERS:
   - Does this job require German, Dutch, or any blocker language as mandatory?
   - Does this job demand on-site presence in an unacceptable location (Munich, Vienna, Berlin, etc.)?
   - Is this an anti-role (e.g. junior IC coder, classical Scrum Master, micromanaged delivery)?
   - Is the budget capped below commercial boundaries?
2. Uncover UNSPOKEN RED FLAGS:
   - Hidden on-call / weekend burdens, vague scope, legacy maintenance traps, excessive bureaucracy.
3. Compute a TRAP SCORE (0 = Safe Opportunity, 100 = Career Trap).
4. Deliver your PROSECUTOR VERDICT:
   - KILL (Fatal dealbreaker present - must not apply)
   - CHALLENGE_SEVERELY (Major gaps or ambiguities requiring strict pre-conditions)
   - TOLERATE (Acceptable boundaries, low trap risk)

### TARGET JOB DESCRIPTION:
{jd_text}

### OUTPUT FORMAT:
Return a valid JSON object matching this schema:
```json
{{
  "prosecutor_verdict": "KILL" | "CHALLENGE_SEVERELY" | "TOLERATE",
  "trap_score": 85.0,
  "dealbreakers": [
    {{
      "category": "language" | "commute" | "anti_role" | "budget" | "other",
      "severity": "FATAL" | "HIGH_RISK",
      "description": "Explanation of why this violates boundaries",
      "evidence_snippet": "Exact quote from JD"
    }}
  ],
  "unspoken_red_flags": [
    "Red flag 1",
    "Red flag 2"
  ],
  "summary_indictment": "Executive indictment paragraph explaining why this mandate is risky or unviable."
}}
```
"""


def build_advocate_prompt(jd_text: str, profile: CandidateProfile, indictment_json: str) -> str:
    """Constructs a strategic defense prompt to rebut or pivot around the prosecutor's indictment."""
    
    proof_lines = [f"- {p.category} ({p.label}): {p.evidence}" for p in profile.proof_metrics]
    proof_str = "\n".join(proof_lines)

    return f"""### ROLE: THE OPPORTUNITY ADVOCATE (EXECUTIVE TALENT AGENT & STRATEGIST)
You are an elite talent strategist and high-stakes executive negotiator representing {profile.full_name}.
Your mission is to maximize commercial leverage, position the candidate at the highest possible value, and counter or pivot around objections.

### CANDIDATE CREDENTIALS & VERIFIED TELEMETRY:
- Name: {profile.full_name}
- Core Identity: {profile.headline} ({profile.scope.seniority})
- Target Scope: {", ".join(profile.scope.primary_titles)}
- Verified Metric Proofs:
{proof_str}
- Languages: {", ".join(profile.languages.fluent_languages)}
- Commercial Target: {profile.commercials.freelance_tjm_eur}

### THE PROSECUTOR\'S RISK INDICTMENT (OBJECTIONS TO ADDRESS):
{indictment_json}

### YOUR MISSION:
Review the Job Description and the Prosecutor\'s Indictment:
1. If the Prosecutor identified a FATAL linguistic or physical commute dealbreaker that CANNOT be solved:
   - You MUST CONCEDE gracefully (verdict: CONCEDE_DEALBREAKER).
2. If the Prosecutor flagged an Anti-Role, Scope Mismatch, or Compensation Gap:
   - PROPOSE A HIGH-VALUE PIVOT (verdict: PIVOT_AND_UPSKILL).
   - Reframe the candidate not as an operational resource, but as a strategic transformation partner.
3. If the Prosecutor only flagged minor red flags:
   - EXPLOIT PERFECT FIT (verdict: EXPLOIT_PERFECT_FIT).
4. Select the TOP 2-3 VERIFIED TELEMETRY PROOFS from the candidate profile that directly solve the employer\'s acute pain.
5. Formulate a killer negotiation opening hook for the hiring manager.

### TARGET JOB DESCRIPTION:
{jd_text}

### OUTPUT FORMAT:
Return a valid JSON object matching this schema:
```json
{{
  "advocate_verdict": "EXPLOIT_PERFECT_FIT" | "PIVOT_AND_UPSKILL" | "CONCEDE_DEALBREAKER",
  "rebuttal_points": [
    "Rebuttal or pivot argument addressing prosecutor objection 1",
    "Rebuttal or pivot argument addressing prosecutor objection 2"
  ],
  "leverage_points": [
    "Why the client desperately needs candidate scale / experience"
  ],
  "grounded_proof_citations": [
    "Exact metric cited from candidate proof metrics"
  ],
  "target_positioning": "Strategic umbrella title (e.g. AI Delivery & Operating Model Architect)",
  "negotiation_hook": "A 3-sentence high-impact outreach hook anchoring on verified metrics."
}}
```
"""
