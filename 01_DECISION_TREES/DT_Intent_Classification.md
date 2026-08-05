# DT: Intent Classification Decision Tree

## Purpose
Provides rule-based classification logic for resolving ambiguous candidate queries into deterministic Intent IDs.

---

## Intent Trigger Keyword Taxonomy

```
                       User Input Query
                              │
       ┌──────────────────────┼──────────────────────┐
       ▼                      ▼                      ▼
  Document Action?      Strategic Request?      Target Match?
       │                      │                      │
  ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
  ▼         ▼            ▼         ▼            ▼         ▼
"Review"  "Rewrite"   "Pivot"   "Salary"     "Job vs CV" "ATS Check"
  │         │            │         │            │           │
  ▼         ▼            ▼         ▼            ▼           ▼
INT-01    INT-02       INT-05    INT-11       INT-07      INT-03
```

---

## Detailed Trigger Rules

- **INT-01 (Resume Review)**
  - Keywords: *"grade my cv"*, *"review resume"*, *"critique"*, *"feedback on resume"*, *"score my cv"*.
  - Rule: If candidate uploads resume without specific target job or instruction, default to INT-01.

- **INT-02 (Resume Rewrite)**
  - Keywords: *"rewrite"*, *"tailor resume"*, *"rebuild CV"*, *"optimize for this job"*.
  - Rule: Triggered when candidate provides a target role or job description alongside a resume.

- **INT-03 (ATS Optimization)**
  - Keywords: *"ATS score"*, *"applicant tracking"*, *"parse error"*, *"ATS keywords"*, *"pass ATS"*.

- **INT-04 (Hidden Opportunities)**
  - Keywords: *"what jobs can I do"*, *"other titles"*, *"alternative roles"*, *"what am I qualified for"*.

- **INT-05 (Career Pivot)**
  - Keywords: *"switch careers"*, *"pivot to"*, *"transition from X to Y"*, *"break into tech"*.

- **INT-06 (Transferable Skills)**
  - Keywords: *"transferable skills"*, *"non-traditional background"*, *"skills crosswalk"*.

- **INT-07 (Job Match Analysis)**
  - Keywords: *"compare resume to JD"*, *"match percentage"*, *"fit audit"*, *"am I qualified for this"*.

- **INT-08 (LinkedIn Optimization)**
  - Keywords: *"LinkedIn profile"*, *"LinkedIn headline"*, *"recruiter reach"*, *"SSI score"*.

- **INT-09 (Cover Letter)**
  - Keywords: *"cover letter"*, *"application letter"*, *"motivation letter"*.

- **INT-10 (Executive Biography)**
  - Keywords: *"executive bio"*, *"leadership summary"*, *"board bio"*.

- **INT-11 (Salary & Positioning)**
  - Keywords: *"negotiate offer"*, *"salary benchmark"*, *"compensation package"*, *"counter offer"*.

- **INT-12 (Interview Preparation)**
  - Keywords: *"interview questions"*, *"STAR method"*, *"mock interview"*, *"interview prep"*.

- **INT-13 (Job Search Strategy)**
  - Keywords: *"30 60 90 plan"*, *"outreach"*, *"job search roadmap"*, *"application strategy"*.

- **INT-14 (Industry Opportunity)**
  - Keywords: *"AI disruption"*, *"growing industries"*, *"industry outlook"*, *"remote market"*.

---

## Related Files & Dependencies
- **Dispatcher Engine**: `00_CORE/CORE_Intent_Dispatcher.md`
- **Workflow Router**: `01_DECISION_TREES/DT_Workflow_Selection.md`
