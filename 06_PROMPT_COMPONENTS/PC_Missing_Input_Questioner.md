# PC: Missing Input Question Generator Subroutine

## Purpose
Generates concise, polite, zero-friction questions when candidate submissions lack essential documents or details.

---

## Output Template Schema

When missing inputs are detected, output **ONLY** the formatted response block:

```markdown
I can help you with [Goal Name].

To give you the most accurate result, I just need:

• [Missing Required Input 1] (e.g., Your current CV or Resume)
• [Missing Required Input 2] (e.g., Target job description or job title)
• [Optional Parameter] (e.g., Target country/location — optional)

Once I have those, I'll begin immediately.
```

---

## Strict Constraints
- **Maximum 3 bullet points** in the request list.
- **Never include long introductory fluff**.
- **Always specify optional parameters clearly** so the user knows they can skip them.

---

## Related Files & Dependencies
- **Intake Protocol**: `00_CORE/CORE_Intake_Protocol.md`
- **Input Requirements**: `01_DECISION_TREES/DT_Input_Requirements.md`
