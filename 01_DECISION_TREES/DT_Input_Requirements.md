# DT: Input Requirements Matrix

## Purpose
Specifies the exact input validation checks executed by `00_CORE/CORE_Intake_Protocol.md` to ensure data completeness before workflow launch.

---

## Input Validation Logic Table

```
Intent ID ──► Check Required Inputs ──► All Present? ──► [YES] ──► Launch Workflow
                                              │
                                           [NO]
                                              ▼
                                   Format Missing Questions
```

---

## Per-Workflow Input Requirements

| Workflow | Mandatory Input(s) | Fallback / Default if Missing |
| :--- | :--- | :--- |
| `WF_Resume_Analyzer.md` | Candidate Resume/CV | Prompt user for CV |
| `WF_Resume_Rewriter.md` | Candidate Resume, Target Job Description | Ask user for Target Job Title if full JD unavailable |
| `WF_Resume_JD_Matcher.md` | Candidate Resume, Target Job Description | Cannot execute without full JD text |
| `WF_ATS_Keyword_Optimizer.md` | Candidate Resume, Target Job Description | Extract keywords from Target Job Title if JD missing |
| `WF_Career_Pivot_Planner.md` | Candidate Resume, Target Pivot Field | Prompt user for target industry/role |
| `WF_Transferable_Skills_Translator.md` | Candidate Resume | Default to general industry mapping |
| `WF_Hidden_Role_Finder.md` | Candidate Resume | Default to adjacent role lookup |
| `WF_LinkedIn_Optimizer.md` | Resume or LinkedIn Text | Prompt user for current profile text |
| `WF_Interview_Preparation.md` | Target Job Description or Role | Ask candidate for top 3 interview concerns |
| `WF_Salary_Negotiation.md` | Offer Details, Target Location | Ask for salary band or target level |
| `WF_Job_Search_OS.md` | Resume, Target Role Title | Default to 30-day generic sprint framework |

---

## Related Files & Dependencies
- **Intake Engine**: `00_CORE/CORE_Intake_Protocol.md`
- **Question Generator**: `06_PROMPT_COMPONENTS/PC_Missing_Input_Questioner.md`
