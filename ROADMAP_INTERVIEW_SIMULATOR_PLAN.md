# Implementation Plan: Interactive Mock Interviewer & Coaching Harness (`careeros_cli.py interview <JD>`)

We will implement an **Interactive Mock Interviewer & Coaching Harness** in CareerOS.

While CareerOS already scores JDs, checks negative constraints, synthesizes custom resumes, and generates probing interview questions, candidates currently lack a live, structured training harness to rehearse high-stakes executive and technical interviews before speaking with real clients or hiring managers.

The new `interview` subsystem turns CareerOS into an interactive, multi-round sparring partner. The agent adopts the persona of a demanding Hiring Manager (e.g. VP of Engineering, Head of Transformation, or Enterprise Architect), conducts a 5-question interview turn-by-turn in the terminal, evaluates candidate answers in real time against strict rubrics (clarity, grounded telemetry, governance posture, answer conciseness), and compiles an actionable **Executive Interview Scorecard & Preparation Debriefing** (`cache/interviews/<JD_ID>_<profile>_debrief.md`).

---

## Architecture: Interactive Sparring Loop

```mermaid
graph TD
    JD["Target Opportunity (e.g. JD_30) + Candidate Profile"] --> QuestionGenerator["1. High-Stakes Question Formulator (5 Strategic Probes)"]
    
    subgraph Live Terminal Interview Session (Turn-by-Turn)
        QuestionGenerator --> AskQ["Interviewer Agent asks Question N"]
        AskQ --> UserAnswer["Candidate inputs Answer (Text / Speech-to-text)"]
        UserAnswer --> TurnCritic["2. Real-Time Critic (Grounded Telemetry, STAR Method, Red Flags)"]
        TurnCritic --> NextQ["Follow-up Probe or Next Question (1..5)"]
    end
    
    subgraph Debriefing & Scorecard Synthesis (engine/interview/debrief.py)
        NextQ --> Scorecard["3. 4-Pillar Interview Scorecard (0-100)"]
        Scorecard --> ActionPlan["4. Verbal Refinements & Better Formulations"]
        ActionPlan --> DebriefMD["cache/interviews/<JD_ID>_<profile>_debrief.md"]
        DebriefMD --> CRMSync["Update Opportunity Stage to INTERVIEWING in Pipeline CRM"]
    end
```

---

## User Review Required

> [!IMPORTANT]
> - **Interactive Terminal Loop (`careeros_cli.py interview <JD>`)**:
>   - The session runs in the user's terminal with Rich formatting.
>   - The agent poses 5 targeted questions spanning:
>     1. **Technical & Domain Depth**: Deep-dive into technical architecture, agentic tools, or cloud scale.
>     2. **Operating Model & Scale**: Handling multi-squad friction, dependencies, and delivery velocity.
>     3. **Governance & Risk**: Handling compliance, EU AI Act, code defect leakage, or security gates.
>     4. **Stakeholder Alignment & Pushback**: Managing difficult C-level executives or skeptical engineers.
>     5. **Commercial Impact & ROI**: Justifying the senior daily rate (TJM) through tangible business outcomes.
> - **Real-Time Evaluation Rubric**:
>   - For each answer, the critic rates:
>     - **STAR Structure** (Situation, Task, Action, Result).
>     - **Telemetry Grounding** (Did the candidate cite verified metrics from their profile, e.g., 7 squads, 50 engineers, $450k FinOps savings, 12 EKS clusters, rather than generic buzzwords?).
>     - **Conciseness & Posture** (Did the candidate sound like an authoritative advisor or an insecure task-worker?).
> - **Fast Simulation vs Live Interactive Mode**:
>   - `--interactive` (default): Asks questions one-by-one in the terminal, waiting for user input.
>   - `--simulate` (for automated testing / benchmark CI): Simulates an automated candidate answering to test the interviewer and scorer end-to-end in seconds.

---

## Proposed Changes

### Component 1: Interview Models & Schemas (`engine/interview/`)

#### [NEW] `engine/interview/models.py`
- Pydantic models:
  - `InterviewQuestion`: Question number, category (Technical, Scale, Governance, Executive, Commercial), probe text, and what the hiring manager is secretly evaluating (*undercover intent*).
  - `AnswerEvaluation`: Score (0-20), strengths identified, missed proof metrics, conciseness rating, red flags detected, and recommended re-framing.
  - `InterviewSessionRecord`: Full transcript of all 5 Q&A pairs, per-question scores, overall interview score (0-100), and debriefing recommendations.

---

### Component 2: Interviewer Persona & Coaching Engine (`engine/interview/coach.py`)

#### [NEW] `engine/interview/coach.py`
- `InterviewCoach`:
  - Generates 5 tailored probing questions bound to the JD requirements and the candidate profile's verified proof telemetry.
  - Scores candidate answers turn-by-turn using the 5 Quality Gates philosophy.
  - Generates an executive debriefing report:
    `cache/interviews/<JD_ID>_<profile>_debrief.md`.

---

### Component 3: CLI Integration & Terminal UI (`careeros_cli.py`)

#### [MODIFY] `careeros_cli.py`
- Add `interview` subcommand:
  ```bash
  py -3.13 careeros_cli.py interview JD_30 [--profile alaa_roucadi] [--simulate] [--model <model>]
  ```
- Renders:
  - Welcome card with Hiring Manager background persona.
  - Turn-by-turn interactive prompt:
    `[Hiring Manager]: <Question>`
    `[Candidate]: <Interactive input>`
    `[Coach Feedback]: Score + Strong Points + What to avoid`
  - Final Rich scorecard table and path to the saved debriefing report.
  - Transitions pipeline stage to `INTERVIEWING` in `pipeline_state.json`.

---

## Verification Plan

### Automated Tests
1. **Simulated Interview Run on JD_30 (Alaa Roucadi)**:
   ```bash
   py -3.13 careeros_cli.py interview JD_30 --profile alaa_roucadi --simulate
   ```
   - Verifies generation of 5 strategic questions.
   - Evaluates 5 simulated answers.
   - Asserts generation of `cache/interviews/JD_30_alaa_roucadi_debrief.md`.
2. **Cross-Profile Verification (Sophie Laurent)**:
   ```bash
   py -3.13 careeros_cli.py interview PERFECT_AWS_DEVOPS_LEAD --profile sophie_cloud_architect --simulate
   ```
   - Asserts that questions focus on Kubernetes, ArgoCD, and Graviton metrics.
3. **Pipeline State Transition**:
   - Check `pipeline_state.json` to verify that `JD_30` transitions to `INTERVIEWING`.
4. **Benchmark Suite Non-Regression**:
   - Run `py -3.13 careeros_cli.py benchmark` to confirm 10/10 PASS.
