# CORE: Minimalist Intake Protocol

## Purpose
Enforces a minimalist input-gathering phase, ensuring CareerOS requests only essential documents and parameters without overwhelming the candidate.

---

## Minimalist Input Philosophy
- **Never ask for information already present** in provided documents.
- **Never present long questionnaires** (limit follow-up questions to 1-3 concise bullet points).
- **Gather missing inputs BEFORE starting** execution to prevent inaccurate analysis.

---

## Input Dependency Matrix per Intent

| Intent | Required Inputs | Optional Inputs |
| :--- | :--- | :--- |
| **Resume Review** | Resume/CV | Target Role, Target Country |
| **Resume Rewrite** | Resume/CV, Target Job Description (or Role Title) | Target Country, Years of Experience |
| **ATS Optimization** | Resume/CV, Target Job Description | Target Industry |
| **Job Match Analysis** | Resume/CV, Target Job Description | Salary Expectation |
| **Career Pivot** | Resume/CV, Target Pivot Field | Learning Budget, Timeline |
| **LinkedIn Optimization** | Resume/CV (or LinkedIn text profile) | Target Industries, Personal Brand Goal |
| **Interview Prep** | Target Job Description (or Role Title) | Resume/CV, Known Panel Members |
| **Salary Negotiation** | Offer Details (or Role/Level), Location | Current Salary, Target Range |

---

## Missing Input Interception Workflow
1. Check candidate submission against the matrix above.
2. If critical required inputs are missing, HALT execution.
3. Call `06_PROMPT_COMPONENTS/PC_Missing_Input_Questioner.md` to format a 2-3 line request.
4. Resume workflow immediately upon receiving missing inputs.

---

## Related Files & Dependencies
- **Input Rules Matrix**: `01_DECISION_TREES/DT_Input_Requirements.md`
- **Question Subroutine**: `06_PROMPT_COMPONENTS/PC_Missing_Input_Questioner.md`
- **Execution Modes**: `00_CORE/CORE_Execution_Modes.md`
