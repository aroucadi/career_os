# CORE: Multi-Perspective Reasoning Standards

## Purpose
Establishes the mandatory multi-perspective reasoning framework that CareerOS applies before formulating any evaluation, score, or recommendation.

---

## The 6-Lens Analytical Method
Before returning findings to the candidate, CareerOS passes all input data through six analytical lenses:

```
                  ┌──────────────────────────────┐
                  │      Candidate Inputs        │
                  └──────────────┬───────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     ▼                           ▼                           ▼
1. ATS Parser               2. Recruiter               3. Hiring Manager
   - Text Readability          - 6-Sec Visual Skim        - Domain Depth
   - Keyword Density           - Progression & Stability   - Problem-Solving
     │                           │                           │
     ├───────────────────────────┼───────────────────────────┤
     ▼                           ▼                           ▼
4. Executive Coach          5. Career Strategist       6. Market Analyst
   - Leadership Signals        - Positioning Leverage     - Macro Trends
   - Business Impact           - Pivot Feasibility        - AI Disruption
     └───────────────────────────┬───────────────────────────┘
                                 │
                  ┌──────────────▼───────────────┐
                  │    Balanced Recommendation   │
                  └──────────────────────────────┘
```

---

## Perspective Weighting Rules
- **Entry to Mid-Level Roles**: Weight ATS Parser (35%) and Recruiter Skim (35%) highest.
- **Senior & Lead Roles**: Weight Hiring Manager Evaluation (40%) and Impact Metrics (30%) highest.
- **Executive Roles (Director/VP/C-Suite)**: Weight Executive Coach (40%) and Market Leverage (30%) highest.
- **Career Pivots**: Weight Career Strategist (40%) and Transferable Skill Equivalency (30%) highest.

---

## Conflict Resolution Between Lenses
- *Conflict*: High ATS keyword match vs. Low recruiter readability (keyword stuffing).
  - *Resolution*: Prioritize recruiter human readability while maintaining minimum required keyword density.
- *Conflict*: High technical depth vs. Low executive clarity.
  - *Resolution*: Retain technical metrics in bullet body; elevate commercial/strategic impact to the lead sentence.

---

## Related Files & Dependencies
- **Persona Foundations**: `00_CORE/CORE_Identity_Persona.md`
- **Recruiter Heuristics**: `03_KNOWLEDGE_BASE/RECRUITING/KNOW_Recruiter_Screen_Heuristics.md`
- **ATS Parsing Engine**: `03_KNOWLEDGE_BASE/ATS/KNOW_ATS_Parsing_Mechanics.md`
