# DT: Career Level Classifier

## Purpose
Evaluates candidate experience level to dynamically configure execution depth in `00_CORE/CORE_Execution_Modes.md`.

---

## Seniority Classification Logic

```
                        Candidate Experience Analysis
                                      │
       ┌──────────────────────────────┼──────────────────────────────┐
       ▼                              ▼                              ▼
Years of Experience           Scope & Responsibility            Title Keywords
 (0-3 / 3-8 / 8-15 / 15+)     (Individual vs Lead vs P&L)   (Junior, Manager, Director, VP)
       │                              │                              │
       └──────────────────────────────┼──────────────────────────────┘
                                      │
                                      ▼
                       Determine Career Level Grade
```

---

## Career Level Taxonomy & Thresholds

### Level 1: Entry / Early Career (0–3 Years YOE)
- **Indicators**: Individual contributor titles (Associate, Analyst, Junior Specialist), execution focus.
- **Execution Mode**: `QUICK MODE` (Focus on clear formatting, action verbs, quantifying initial impact).

### Level 2: Mid-Career Professional (3–8 Years YOE)
- **Indicators**: Senior titles, project leadership, cross-functional coordination, domain mastery.
- **Execution Mode**: `STRATEGY MODE` (Focus on business metrics, process ownership, domain depth).

### Level 3: Senior / Managerial Lead (8–15 Years YOE)
- **Indicators**: Manager, Lead, Head of, Director titles; team management; budget handling; strategic planning.
- **Execution Mode**: `STRATEGY MODE` / `EXECUTIVE MODE` (Focus on team growth, P&L attribution, strategic impact).

### Level 4: Executive Leadership (15+ Years YOE or C-Suite Target)
- **Indicators**: VP, Senior Director, C-Suite (CEO, CTO, CMO, CFO), Managing Director; company-wide P&L, board reporting.
- **Execution Mode**: `EXECUTIVE MODE` (Focus on governance, shareholder value, multi-million dollar transformation).

---

## Related Files & Dependencies
- **Execution Modes**: `00_CORE/CORE_Execution_Modes.md`
- **Executive Rubric**: `04_RUBRICS/RUBRIC_Executive_Scorecard.md`
