# PC: Weak Bullet Transformer Subroutine

## Purpose
Subroutine converting weak, duty-focused resume bullet points into high-impact, quantified achievement statements using the Google XYZ formula.

---

## Transformation Pipeline

```
[Weak Duty Bullet] ──► Extract Active Action Verb ──► Embed Tool/Method ──► Inject Quantified Metric ($/%)
```

---

## Before & After Transformation Rules

### Example 1: Software Engineering
- ❌ *Before*: *"Responsible for fixing bugs in the database."*
- ✅ *After*: *"Resolved 40+ high-severity database deadlock bugs in PostgreSQL, reducing query error rates by 35% across core checkout services."*

### Example 2: Product Management
- ❌ *Before*: *"Worked with design team to update UI."*
- ✅ *After*: *"Spearheaded mobile app UI redesign in Figma alongside a 4-person design squad, boosting 30-day user retention from 22% to 38%."*

### Example 3: Operations
- ❌ *Before*: *"Managed weekly inventory reports."*
- ✅ *After*: *"Automated weekly warehouse inventory reporting using Python scripts, eliminating 6 manual hours weekly and cutting variance by 18%."*

---

## Related Files & Dependencies
- **Action Verbs**: `06_PROMPT_COMPONENTS/PC_Action_Verbs.md`
- **Impact Quantification**: `03_KNOWLEDGE_BASE/RECRUITING/KNOW_Impact_Quantification.md`
