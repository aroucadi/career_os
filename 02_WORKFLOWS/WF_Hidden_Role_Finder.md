# WF: Hidden Role Finder Workflow

## Purpose
Execution pipeline for discovering 15–25 realistic, non-obvious job titles based on candidate skill sets and adjacent industries.

---

## Step-by-Step Execution Protocol

1. **Skill Extraction**: Extract core competencies using `06_PROMPT_COMPONENTS/PC_Skill_Extractor.md`.
2. **Adjacent Cross-Walk**: Query `03_KNOWLEDGE_BASE/MARKET/KNOW_Adjacent_Industry_Mapping.md` to identify adjacent functional roles.
3. **Role Expansion Matrix**: Generate 15–25 matching role titles across 3 tiers:
   - *Direct Title Matches* (6–8 roles).
   - *Adjacent Functional Roles* (6–8 roles).
   - *Emerging / Niche AI Roles* (3–5 roles).
4. **Attribute Scoring**: For each title, compute:
   - **Match %** (0–100%).
   - **Salary Potential** ($ range).
   - **Market Demand** (High / Medium / Low).
   - **Competition Level** (High / Medium / Low).
   - **Ease of Entry** (High / Medium / Low).
   - **Why It Fits** (1-sentence rationale).

---

## Related Files & Dependencies
- **Adjacent Industries**: `03_KNOWLEDGE_BASE/MARKET/KNOW_Adjacent_Industry_Mapping.md`
- **Skill Extractor**: `06_PROMPT_COMPONENTS/PC_Skill_Extractor.md`
