# KNOW: ATS Keyword Density & Semantic Matching

## Purpose
Explains keyword extraction algorithms, hard skill vs. soft skill indexing, and TF-IDF semantic relevance scoring in recruiting search engines.

---

## Keyword Weighting & Matching Mechanics

Modern ATS platforms rank candidates using a weighted search vector:

$$\text{Relevance Score} = w_1(\text{Exact Hard Skill Matches}) + w_2(\text{Title Matches}) + w_3(\text{Semantic Synonyms}) - w_4(\text{Stuffing Penalty})$$

```
                   Target Job Description
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
Required Hard Skills    Job Title Keywords     Contextual Acronyms
  (e.g., Python, SQL)   (e.g., Data Engineer)     (e.g., AWS, GCP, CI/CD)
```

---

## Hard Skills vs. Soft Competencies

- **Hard Skills (Weight: High, 70%)**: Software tools, programming languages, methodologies, certifications, regulatory knowledge.
- **Soft Competencies (Weight: Low, 10%)**: Communication, leadership, problem-solving, collaboration. (Soft skills are evaluated by recruiters, not ATS search queries).

---

## Natural Keyword Insertion Rules

- **Context Matters**: Keywords must appear within meaningful sentences or skill sections (e.g., *"Engineered data pipelines using Python and Spark"* > *"Python, Spark, SQL"*).
- **Exact Matches & Acronyms**: Include both full spelled-out terms and standard acronyms (e.g., *"Amazon Web Services (AWS)"*, *"Search Engine Optimization (SEO)"*).
- **Frequency**: Maintain 2–4 occurrences of primary core hard skills across summary and work experience; avoid artificial repetition.

---

## Related Files & Dependencies
- **ATS Keyword Optimizer Workflow**: `02_WORKFLOWS/WF_ATS_Keyword_Optimizer.md`
- **ATS Scorecard**: `04_RUBRICS/RUBRIC_ATS_Scorecard.md`
