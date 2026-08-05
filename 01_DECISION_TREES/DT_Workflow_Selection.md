# DT: Workflow Selection & Chaining Logic

## Purpose
Defines single and multi-step workflow chaining logic when a candidate objective spans multiple functional tools.

---

## Single Workflow Direct Routing

```
Intent Classification
       │
       ├── INT-01 ──► WF_Resume_Analyzer.md
       ├── INT-02 ──► WF_Resume_Rewriter.md
       ├── INT-05 ──► WF_Career_Pivot_Planner.md
       ├── INT-07 ──► WF_Resume_JD_Matcher.md
       ├── INT-08 ──► WF_LinkedIn_Optimizer.md
       ├── INT-11 ──► WF_Salary_Negotiation.md
       └── INT-12 ──► WF_Interview_Preparation.md
```

---

## Multi-Workflow Chaining Protocols

### Chained Suite 1: Full Job Application Overhaul
- **Trigger**: User asks to *"completely tailor my materials for this role"*.
- **Execution Chain**:
  1. `WF_Resume_JD_Matcher.md` (Extract gap analysis & score baseline).
  2. `WF_ATS_Keyword_Optimizer.md` (Extract required keywords).
  3. `WF_Resume_Rewriter.md` (Generate tailored resume).
  4. `TPL_Cover_Letters.md` (Generate targeted 3-paragraph letter).

### Chained Suite 2: Complete Executive Re-Positioning
- **Trigger**: Executive candidate preparing for a market search.
- **Execution Chain**:
  1. `WF_Executive_Branding.md` (Define strategic value proposition).
  2. `TPL_Resume_Executive.md` (Produce C-suite executive resume).
  3. `TPL_Executive_Bio.md` (Generate one-page executive biography).
  4. `WF_LinkedIn_Optimizer.md` (Align LinkedIn branding).

### Chained Suite 3: Career Pivot Launchpad
- **Trigger**: Candidate changing fields with no direct experience.
- **Execution Chain**:
  1. `WF_Transferable_Skills_Translator.md` (Extract core competencies).
  2. `DT_Pivot_Viability.md` (Assess gap & success probability).
  3. `WF_Career_Pivot_Planner.md` (Formulate 5 transition paths).
  4. `TPL_Resume_Functional_Pivot.md` (Draft hybrid pivot resume).

---

## Related Files & Dependencies
- **Intent Dispatcher**: `00_CORE/CORE_Intent_Dispatcher.md`
- **Workflows**: `02_WORKFLOWS/*`
