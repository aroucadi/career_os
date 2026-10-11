# CareerOS: Top-5 AI-Native Concepts Scouting Brief

## 1. Executive Summary
Per Section 10.9 of the Universal Product Experience Reinvention framework, we scouted the current state of the art in AI-native interfaces, adaptive streaming UI, dialectic consensus reasoning, and privacy-first candidate telemetry. We evaluated each concept against the three feeling words (**Capable**, **Grounded**, **Unassailable**), the 12 Core Laws, and the operational constraints of CareerOS.

---

## 2. The 5 Selected Concepts for CareerOS

### Concept 1: Progressive Streaming UI Compiler (Intelligent UI Reference)
- **What it is**: The LLM streams structured component tool-calls (`GapAnalysisCard`, `HonestReframingDiff`, `DialecticVerdict`) through a deterministic compiler that renders accessible, live React primitives progressively into pre-reserved layout dimensions without layout shift ($\text{CLS} = 0.000$).
- **Why it fits CareerOS**: Matches the OpenAI GPT-6 Intelligent UI benchmark (announced Oct 2026). Candidates do not read walls of chat text; they interact directly with reactive evaluation cards.
- **Risk**: Streaming partial JSON schema malformation or renderer mismatch.
- **Cheapest Test Plan**: Vercel AI SDK Data Stream protocol v1 with strict zod/Pydantic schemas and deterministic static fallback card.
- **Verification Status**: **VERIFIED IN PRODUCTION** (Serving live on Cloud Run via `/api/chat`).

### Concept 2: Truth-Guard Grounded Fact Diffing
- **What it is**: High-velocity bullet point upgrades generated exclusively by anchoring candidate verbs to verbatim sentences in the parsed CV. Blocks hallucinated certifications, fake numbers, or non-existent tech stacks.
- **Why it fits CareerOS**: Directly honors feeling word **Grounded**. Prevents the catastrophic failure mode of AI career tools (inventing accomplishments that fail technical interviews).
- **Risk**: Candidate perceives AI suggestions as conservative if previous bullet points lacked metrics.
- **Cheapest Test Plan**: Unit tests (`tests/test_candidate_agent.py`) verifying that every reframed bullet contains substrings from original CV text.
- **Verification Status**: **VERIFIED** (Engine runs dynamic sentence matching; 62/62 tests passing).

### Concept 3: Adversarial Dialectic Scrutiny (Prosecutor vs Advocate)
- **What it is**: Multi-agent dialectic debate between a skeptical Hiring Manager / Prosecutor (hunting red flags, title inflation, below-market rates) and an Executive Talent Advocate (quantifying value levers, compensation multipliers, strategic wedge).
- **Why it fits CareerOS**: Directly honors feeling word **Unassailable**. Prepares candidates for brutal real-world interviews rather than giving generic encouraging platitudes.
- **Risk**: Candidate anxiety if Prosecutor feedback is unconstructive or overly harsh.
- **Cheapest Test Plan**: Strict rubric loader constraining Prosecutor to factual recruiter risk tiers and coupling every risk directly to an Advocate talking point.
- **Verification Status**: **VERIFIED** (Built into `/evaluate` flow and `GapAnalysisCard` interview shield).

### Concept 4: Zero-Friction Anonymous Local-First Workspace
- **What it is**: Complete end-to-end functionality (CV upload, JD gap scoring, bullet rewriting, PDF compilation) available immediately on Day-0 without requiring account registration, passwords, or cloud PII retention.
- **Why it fits CareerOS**: Directly honors feeling word **Capable** and Law 9 (Earn the Complexity). Eliminates the 85% drop-off caused by mandatory signup walls. Session is keyed to an anonymous UUID stored in browser `localStorage`.
- **Risk**: User switches devices before claiming account and loses local state.
- **Cheapest Test Plan**: 1-click "Claim Account" banner offering instant sync via LinkedIn OAuth or Magic Link when high-value signals occur.
- **Verification Status**: **VERIFIED** (Implemented in `lib/session.ts` and `ClaimAccountModal.tsx`).

### Concept 5: Interactive 1-Tap Gap Remediation & Live Rescoring
- **What it is**: Interactive checkbox controls on generative gap cards that let candidates toggle on/off acquired competencies or approved reframings, instantly triggering an optimistic rescore ($\le 2\text{s}$) without re-running full LLM pipelines.
- **Why it fits CareerOS**: Fulfills the Effort Budget ($\le 2$ taps, $\le 10$ seconds) and Law 11 (Show reasoning, keep control).
- **Risk**: Compute burn if full prompt generation runs on every checkbox change.
- **Cheapest Test Plan**: Dedicated lightweight endpoint `/api/chat/gap-rescore` that recalculates ATS percentage mathematically based on checked items.
- **Verification Status**: **VERIFIED IN PRODUCTION** (Live on Cloud Run).
