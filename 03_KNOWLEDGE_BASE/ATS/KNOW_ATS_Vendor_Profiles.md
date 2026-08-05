# KNOW: Major ATS Vendor Parsing Profiles

## Purpose
Catalog of parsing behaviors, search ranking mechanics, and quirks across major commercial Applicant Tracking Systems.

---

## Vendor Ecosystem Matrix

### 1. Greenhouse
- **Behavior**: Minimalist parser; relies heavily on recruiter manual review. Stores candidate documents as native PDFs.
- **Key Focus**: Structured interview rubrics, custom job application fields, clean visual layout for human skimmers.
- **Risk Area**: Highly dependent on clear bullet points for recruiter 6-second scan.

### 2. Workday
- **Behavior**: Heavy enterprise parsing engine; auto-populates complex candidate profile fields during application submission.
- **Key Focus**: Exact section header matching, strict date parsing (`Month YYYY`), explicit skill extraction.
- **Risk Area**: Custom graphics or tables cause misaligned field population, frustrating applicants.

### 3. Lever
- **Behavior**: Modern, CRM-driven pipeline. Groups candidates by source (Applied, Sourced, Referred).
- **Key Focus**: Plain text extraction, fast keyword search across candidate profile notes, clean single-column PDF renders.

### 4. Taleo (Oracle Enterprise)
- **Behavior**: Legacy enterprise parser; highly rigid boolean search engine.
- **Key Focus**: Exact keyword string matches, exact job title matches, strict education credentials.
- **Risk Area**: Rejects non-standard headers or complex formatting with low match scores.

### 5. iCIMS
- **Behavior**: Robust mid-market/enterprise parser with AI match scoring modules.
- **Key Focus**: Contextual skill extraction, semantic matching, employment gap highlighting.

---

## Related Files & Dependencies
- **ATS Parsing Mechanics**: `03_KNOWLEDGE_BASE/ATS/KNOW_ATS_Parsing_Mechanics.md`
- **ATS Scorecard**: `04_RUBRICS/RUBRIC_ATS_Scorecard.md`
