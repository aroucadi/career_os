# WF: Resume Rewriter Execution Workflow

## Purpose
End-to-end execution pipeline for reconstructing a candidate's resume tailored to a target position or seniority level.

---

## Step-by-Step Execution Protocol

1. **Input Validation**: Verify presence of CV and Target Job Description using `00_CORE/CORE_Intake_Protocol.md`.
2. **Template Selection**: Query candidate seniority to select target layout from `05_TEMPLATES/RESUME/*`.
3. **Summary Reconstruction**: Draft high-impact Professional Summary containing target role title, years of experience, core technical stack, and key career metric anchor.
4. **Experience Overhaul**: Pass every bullet through `06_PROMPT_COMPONENTS/PC_Bullet_Transformer.md`:
   - Replace passive verbs with active verbs from `06_PROMPT_COMPONENTS/PC_Action_Verbs.md`.
   - Embed Google XYZ formula metrics ($ / % / scale).
   - Inject required hard keywords naturally.
5. **Anti-Fabrication Check**: Verify no false qualifications or exaggerated metrics were introduced.
6. **Final Deliverable Render**: Produce complete, publication-ready Markdown resume.

---

## Related Files & Dependencies
- **Bullet Transformer**: `06_PROMPT_COMPONENTS/PC_Bullet_Transformer.md`
- **Action Verbs**: `06_PROMPT_COMPONENTS/PC_Action_Verbs.md`
- **Resume Templates**: `05_TEMPLATES/RESUME/*`
