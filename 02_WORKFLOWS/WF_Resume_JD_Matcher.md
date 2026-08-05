# WF: Resume vs. Job Description Matcher Workflow

## Purpose
Comparative gap analysis engine evaluating candidate CV against a target job posting, producing a quantitative gap matrix.

---

## Step-by-Step Execution Protocol

1. **Requirement Extraction**: Parse Job Description to isolate Hard Requirements, Soft Competencies, and Preferred Qualifications.
2. **Match Verification**: Search candidate CV for direct evidence of each extracted requirement.
3. **Comparative Matrix Generation**: Construct 5-column audit table:
   - **Job Requirement**: Parameter from JD.
   - **Match Status**: Exact Match / Partial Match / Missing.
   - **CV Evidence**: Quoted text or section location.
   - **Gap Analysis**: What is missing or weak.
   - **Recommended Fix**: Resume update or interview framing.
4. **Score Output**:
   - **Overall Match Fit %**.
   - **Estimated Interview Callback Probability %**.
   - **ATS Keyword Match Score**.

---

## Related Files & Dependencies
- **Job Match Scorer**: `04_RUBRICS/RUBRIC_Job_Match_Scorer.md`
- **ATS Keyword Semantics**: `03_KNOWLEDGE_BASE/ATS/KNOW_ATS_Keyword_Semantics.md`
