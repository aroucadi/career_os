# KNOW: ATS Parsing Mechanics & Architectural Rules

## Purpose
Provides technical domain knowledge on how Applicant Tracking System (ATS) parsing engines process text, extract resume entities, and structure candidate data.

---

## Technical Parsing Architecture

Commercial ATS parsers (e.g., Sovren, DaXtra, Textkernel) parse documents via sequential token extraction:

```
[Raw Document File (PDF/DOCX)]
              │
              ▼
    1. Text Extraction Layer (OCR & Character Encoding Normalization)
              │
              ▼
    2. Section Header Identification (Regex & Named Entity Recognition)
              │
              ▼
    3. Entity Extraction & Classification (Titles, Dates, Companies, Skills)
              │
              ▼
    4. Structured Candidate JSON Schema Generation
```

---

## Parsing Failure Modes & Causes

1. **Multi-Column Layout Confusion**: Parsers read across columns left-to-right, scrambling separate text blocks into incoherent sentences.
2. **Table & Graphic Omission**: Text embedded inside tables, text boxes, canvas elements, or images is frequently ignored or dropped.
3. **Non-Standard Section Header Failure**: Headers like *"Where I've Been"* or *"My Story"* fail header recognition, placing bullets under the wrong category.
4. **Header/Footer Dropping**: Contact details placed inside Word/PDF page headers or footers are frequently stripped by text extractors.

---

## Recommended Formatting Standards

- **Layout**: Single-column layout exclusively.
- **Section Headers**: Standardized names (`Work Experience`, `Education`, `Skills`, `Professional Summary`).
- **File Format**: Plain DOCX or text-based PDF (avoid flattened PDF scans).
- **Fonts**: Standard system fonts (Arial, Calibri, Helvetica, Times New Roman, Garamond).

---

## Related Files & Dependencies
- **Formatting Rules**: `03_KNOWLEDGE_BASE/ATS/KNOW_ATS_Formatting_Rules.md`
- **ATS Scorecard**: `04_RUBRICS/RUBRIC_ATS_Scorecard.md`
- **ATS Vendor Details**: `03_KNOWLEDGE_BASE/ATS/KNOW_ATS_Vendor_Profiles.md`
