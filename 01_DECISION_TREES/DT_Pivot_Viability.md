# DT: Career Pivot Viability Decision Tree

## Purpose
Provides rule-based viability scoring to assess candidate readiness for a requested career transition before building roadmaps.

---

## Pivot Risk Evaluation Framework

```
                          Pivot Request Evaluation
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
  Skill Overlap Ratio        Industry Barrier Index      Retraining Requirement
  (Direct vs Transferable)    (Strict vs Accessible)     (Self-study vs Certification)
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
                                     ▼
                        Calculate Pivot Viability Grade
```

---

## Viability Scoring Logic

1. **High Viability (Score: 80–100%)**
   - Candidate possesses >60% overlapping functional skills.
   - Low barrier to entry in target industry.
   - Example: Software Engineer transitioning from Banking to FinTech, or Operations Specialist moving to Tech Ops.
   - **Recommendation**: Immediate resume re-framing + direct application strategy.

2. **Moderate Viability (Score: 50–79%)**
   - Candidate possesses 30–50% transferable skill overlap.
   - Moderate barrier; requires 3-6 month certification or portfolio project.
   - Example: Marketing Manager moving to Product Management, or Data Analyst moving to Data Science.
   - **Recommendation**: Execute `WF_Career_Pivot_Planner.md` to build bridging portfolio and learning plan.

3. **High-Risk / Low Viability (Score: <50%)**
   - Skill overlap <30%.
   - High institutional barrier (e.g., requires accredited medical/legal credentials or 4-year degree).
   - Example: Graphic Designer attempting to transition directly to Senior Machine Learning Engineer.
   - **Recommendation**: Highlight credential gaps objectively; suggest realistic 2-stage stepping-stone roles.

---

## Related Files & Dependencies
- **Adjacent Industries**: `03_KNOWLEDGE_BASE/MARKET/KNOW_Adjacent_Industry_Mapping.md`
- **Pivot Workflow**: `02_WORKFLOWS/WF_Career_Pivot_Planner.md`
- **Feasibility Rubric**: `04_RUBRICS/RUBRIC_Pivot_Feasibility_Scorer.md`
