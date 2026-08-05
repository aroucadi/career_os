# CORE: Intent Dispatcher Engine

## Purpose
Orchestrates the classification of user requests into one of 14 primary career strategy workflows, determining the appropriate execution pipeline.

---

## Primary Intent Mapping Table

| Intent ID | Intent Name | Primary Goal | Target Workflow |
| :--- | :--- | :--- | :--- |
| **INT-01** | Resume Review | Audit existing CV across ATS, Recruiter, and Executive metrics | `WF_Resume_Analyzer.md` |
| **INT-02** | Resume Rewrite | Tailor resume for a specific job target or level | `WF_Resume_Rewriter.md` |
| **INT-03** | ATS Optimization | Maximize parser compatibility and keyword indexing | `WF_ATS_Keyword_Optimizer.md` |
| **INT-04** | Hidden Opportunities | Uncover non-obvious job titles matching background | `WF_Hidden_Role_Finder.md` |
| **INT-05** | Career Pivot | Plan structured transition to a new role or industry | `WF_Career_Pivot_Planner.md` |
| **INT-06** | Transferable Skills | Map existing capabilities to new domains | `WF_Transferable_Skills_Translator.md` |
| **INT-07** | Job Match Analysis | Quantitative CV vs. Job Description gap audit | `WF_Resume_JD_Matcher.md` |
| **INT-08** | LinkedIn Optimization | Optimize profile searchability, branding, and conversion | `WF_LinkedIn_Optimizer.md` |
| **INT-09** | Cover Letter | Draft targeted, modern 3-paragraph cover letter | `TPL_Cover_Letters.md` |
| **INT-10** | Executive Biography | Craft senior leadership executive bio | `TPL_Executive_Bio.md` |
| **INT-11** | Salary & Positioning | Benchmark compensation and structure negotiation | `WF_Salary_Negotiation.md` |
| **INT-12** | Interview Preparation | Predict questions, structure STAR responses, mock prep | `WF_Interview_Preparation.md` |
| **INT-13** | Job Search Strategy | Build 30/60/90 outbound search campaign and KPIs | `WF_Job_Search_OS.md` |
| **INT-14** | Industry Opportunity | Analyze growth, demand, remote options, and AI risk | `WF_Industry_Opportunity_Scanner.md` |

---

## Ambiguous Intent Resolution Protocol
When user input is vague (e.g., "Help me with my career" or "Look at my resume"):
1. Match query keywords against `01_DECISION_TREES/DT_Intent_Classification.md`.
2. Infer the most likely intent (default to **Resume Review (INT-01)** if a resume is provided).
3. If intent cannot be determined with >80% confidence, execute `00_CORE/CORE_Welcome_Protocol.md` to offer menu options.

---

## Related Files & Dependencies
- **Classification Logic**: `01_DECISION_TREES/DT_Intent_Classification.md`
- **Intake Check**: `00_CORE/CORE_Intake_Protocol.md`
- **Workflow Router**: `01_DECISION_TREES/DT_Workflow_Selection.md`
