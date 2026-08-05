# WF: Resume Analyzer Workflow

## Purpose
Execution pipeline for auditing a candidate's resume across 4 dimensions, returning scores, strengths, weaknesses, quick wins, and high-impact fixes.

---

## Step-by-Step Execution Protocol

```
1. Receive CV ──► 2. Load Rubrics ──► 3. Calculate Vector Scores ──► 4. Generate Audit Report
```

### Step 1: Input Check & Level Assignment
- Load candidate CV text.
- Invoke `01_DECISION_TREES/DT_Career_Level_Classifier.md` to establish seniority tier.

### Step 2: Multi-Vector Scoring
Pass document through rubrics:
- `04_RUBRICS/RUBRIC_ATS_Scorecard.md` → Calculate ATS Parse Score.
- `04_RUBRICS/RUBRIC_Recruiter_Scorecard.md` → Calculate Recruiter Visual Score.
- `04_RUBRICS/RUBRIC_Executive_Scorecard.md` → Calculate Leadership Score (if Senior/Exec).
- `04_RUBRICS/RUBRIC_Composite_Resume_Scorer.md` → Aggregate Overall Score (/100).

### Step 3: Extract Findings
- Identify **Top 3 Core Strengths**.
- Identify **Top 3 Critical Weaknesses**.
- Extract **3 Quick Wins** (fixable in <15 minutes).
- Extract **3 High-Impact Fixes** (requires deeper rewrites or metric additions).

---

## Standard Audit Output Schema

```markdown
## Resume Audit Report

**Overall Score**: [XX]/100
- **ATS Score**: [XX]/100
- **Recruiter Score**: [XX]/100
- **Executive Score**: [XX]/100

### Strengths
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

### Critical Weaknesses
1. [Weakness 1]
2. [Weakness 2]

### Quick Wins (<15 Mins)
• [Quick Win 1]
• [Quick Win 2]

### High-Impact Improvements
• [Improvement 1]
```

---

## Related Files & Dependencies
- **Composite Scorer**: `04_RUBRICS/RUBRIC_Composite_Resume_Scorer.md`
- **Communication Standards**: `00_CORE/CORE_Communication_Standards.md`
