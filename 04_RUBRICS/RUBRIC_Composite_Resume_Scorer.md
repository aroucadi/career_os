# RUBRIC: Composite Resume Scoring Model (/100)

## Purpose
Master weighted scoring model producing an overall /100 grade for candidate resumes across four core evaluation vectors.

---

## Score Weight Distribution

$$\text{Overall Composite Score} = 0.30(\text{ATS Score}) + 0.30(\text{Recruiter Score}) + 0.20(\text{Impact Score}) + 0.20(\text{Target Match Score})$$

---

## Score Band Classification

- **90–100 (Tier 1: Top 5% Applicant)**: Exceptional keyword density, outstanding quantified impact, flawless visual layout. Interview probability >75%.
- **75–89 (Tier 2: Strong Applicant)**: Solid experience, good formatting, clear achievements. Minor quick-win edits required. Interview probability 40–74%.
- **60–74 (Tier 3: Moderate Fit)**: Passing ATS, but weak bullet quantification, passive verb choices, or unoptimized visual skimmability. Interview probability 15–39%.
- **<60 (Tier 4: High Rejection Risk)**: Critical formatting bugs, severe keyword gaps, unquantified task listings. High probability of automatic rejection.

---

## Related Files & Dependencies
- **ATS Scorecard**: `04_RUBRICS/RUBRIC_ATS_Scorecard.md`
- **Recruiter Scorecard**: `04_RUBRICS/RUBRIC_Recruiter_Scorecard.md`
- **Resume Analyzer**: `02_WORKFLOWS/WF_Resume_Analyzer.md`
