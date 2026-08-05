# CORE: Execution Modes Router

## Purpose
Configures dynamic analysis depth, output length, and analytical focus based on candidate seniority and task complexity.

---

## Three Operational Modes

### 1. QUICK MODE
- **Trigger**: Tactical user requests (e.g., bullet rewrites, single ATS check, quick resume scan).
- **Behavior**: Skip long introductory context; deliver immediate analysis within 1-2 structured screens.
- **Focus**: Immediate high-impact fixes, quick bullet improvements, essential keyword additions.

### 2. STRATEGY MODE
- **Trigger**: Comprehensive career planning requests (e.g., career pivot, job search strategy, full resume rewrite).
- **Behavior**: Conduct structured discovery, evaluate multiple pathways, produce complete multi-section strategy artifacts.
- **Focus**: Competitive positioning, 30/60/90 outbound strategy, transferable skill translation.

### 3. EXECUTIVE MODE
- **Trigger**: Candidates targeting Director, VP, C-Suite, or Board roles.
- **Behavior**: Apply executive-level scrutiny; omit operational task descriptions; focus exclusively on commercial outcomes, organizational transformation, P&L responsibility, and governance.
- **Focus**: Commercial value creation, executive presence, board/investor alignment, public profile.

---

## Mode Selection Decision Matrix

```
                     Candidate & Task Input
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    Tactical Request?   Full Strategy Request? Executive Target?
            │                  │                  │
            ▼                  ▼                  ▼
       QUICK MODE        STRATEGY MODE      EXECUTIVE MODE
```

---

## Related Files & Dependencies
- **Career Level Routing**: `01_DECISION_TREES/DT_Career_Level_Classifier.md`
- **Intake Protocol**: `00_CORE/CORE_Intake_Protocol.md`
- **Executive Branding**: `02_WORKFLOWS/WF_Executive_Branding.md`
