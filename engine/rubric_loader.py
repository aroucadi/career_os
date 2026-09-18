"""
CareerOS Rubric & Knowledge Base Loader
=======================================
Dynamically loads and injects rubrics and frameworks from CareerOS root:
- 04_RUBRICS (ATS, Recruiter, Executive, Job Match, Composite)
- 06_PROMPT_COMPONENTS (Bullet Transformer XYZ, Action Verbs, Skill Extractor)
- 03_KNOWLEDGE_BASE (ATS Rules, Recruiter Heuristics, Impact Quantification, Executive Signals)
- 02_WORKFLOWS (Resume Analyzer, Resume JD Matcher, Resume Rewriter)
- EMEA Freelance Contract Intelligence (Rates, Umbrella Titles, C-Suite Deliverables)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_file_content(relative_path: str) -> str:
    path = BASE_DIR / relative_path
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""

def get_injected_rubrics_prompt() -> str:
    """Combines core rubrics into a unified scoring prompt module with Freelance Contract Intelligence."""
    return f"""
=== GENERAL INSTRUCTION EVALUATION FRAMEWORK & RUBRICS ===

--- 1. COMPOSITE SCORING MODEL WEIGHTS ---
Overall Composite Score = 0.30 * ATS_Score + 0.30 * Recruiter_Score + 0.20 * Bullet_Impact_Score + 0.20 * Target_Match_Score

--- 2. ATS TECHNICAL COMPATIBILITY RUBRIC (Max 100 points) ---
- Document Architecture (30 pts): Single column layout, clean markdown/text parseability.
- Section Header Standards (20 pts): Standard headers (Professional Summary, Work Experience, Certifications, Education, Skills).
- Keyword Match Ratio (30 pts): Exact & semantic match of core target hard skills & frameworks.
- Contact / Header Hygiene (10 pts): Email, phone, location, LinkedIn present in standard body header.
- Date & Chronology Format (10 pts): Consistent date formatting without unaccounted gaps.

--- 3. RECRUITER 6-SECOND SCREEN RUBRIC (Max 100 points) ---
- Visual Hierarchy & Skimmability (25 pts): Clean spacing, 2-4 line focused bullets.
- Title Progression & Alignment (25 pts): Strong upward career trajectory matching target role seniority.
- Action Verb Strength (25 pts): High-impact active lead verbs (Architected, Spearheaded, Directed, Deployed, Scaled).
- Quantified Achievement Ratio (25 pts): >60% of bullet points contain explicit metrics ($, %, headcount, sprint velocity, ROI).

--- 4. BULLET IMPACT & GOOGLE XYZ TRANSFORMER RULES ---
Google XYZ Formula: "Accomplished [X], as measured by [Y], by doing [Z]".
- Active action verbs (PC_Action_Verbs)
- Embed explicit tools, frameworks, platforms (Rovo, Claude Code, Azure AI, SAFe, Jira Cloud, LeSS)
- Inject hard metrics (%, time saved, accuracy, squad scale)

--- 5. EXECUTIVE & LEADERSHIP PRESENCE RUBRIC (Max 100 points) ---
- P&L & Fiscal Ownership (30 pts): Budget scope, cost reduction, commercial proposals/avant-ventes contribution.
- Organizational Scale (25 pts): Multi-tribe / multi-squad leadership, headcount (~50 engineers/POs).
- Commercial Strategy & Vision (25 pts): AI strategy, portfolio governance, value realization.
- Governance & Risk Authority (20 pts): EU AI Act risk tiers, responsible AI, human-in-the-loop gates.

--- 6. JOB MATCH & COMPETENCY FIT RUBRIC (Max 100 points) ---
- Hard Technical & Tooling Requirements (50 pts)
- YOE, Leadership & Domain Alignment (30 pts)
- Education & Certifications (20 pts)

--- 7. FREELANCE CONTRACT & C-SUITE POSITIONING RUBRIC (EMEA 2026 Market Benchmark) ---
- Daily Rate Benchmark Alignment (€700–€1,300/day, £600–£1,000/day, CHF 1,100–1,400/day): Evaluate CV against high-ticket freelance expectations.
- Umbrella Title Positioning: Recognize that standalone "AI Adoption" or "Change" roles are subsumed under umbrella titles:
  * "AI Platform Product Manager" / "Head of AI Platform"
  * "AI Delivery Lead & Operating Model Architect"
  * "Directeur de Projet IA & Governance"
- Discrete C-Suite Deliverables:
  * "AI Operating Model & Governance Architecture": Transitioning AI use cases from PoC to production across multi-squad divisions.
  * "Value Stream & Flow Optimization": Auditing software delivery chains to eliminate latency in AI-augmented workflows.
  * "Strategic Portfolio & Flow Telemetry Design": Architecting Jira Cloud/Alignify for executive visibility over capital allocation and throughput.
=============================================================
"""

if __name__ == "__main__":
    print("CareerOS Rubric Prompt Preview:")
    print(get_injected_rubrics_prompt())
