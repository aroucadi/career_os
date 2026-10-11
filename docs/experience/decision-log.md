# CareerOS: Architecture & Experience Decision Log

## Decision 1: Anchor Definition — The Target Mandate (Pipeline / Match Stream)
- **Principle / Skill**: Law 1 (One Anchor, Many Rooms), `pencilplaybook` (Compositional Discipline).
- **Decision**: Anchored the entire interface on the active Job Mandate. All capabilities (Gap, Tailor, Evaluate, Pipeline) enter through this single anchor.
- **Alternatives Rejected**:
  - *The Free-Form Chat Window*: Rejected because users suffer prompt paralysis and get unstructured markdown text dumps.
  - *The 10-Metric KPI Dashboard*: Rejected because Day-0 users have zero data, producing empty graphs and cognitive fatigue.

## Decision 2: Authentication Model — Anonymous Local-First Icebreaker
- **Principle / Skill**: Law 9 (Earn the Complexity), Law 10 (Effort Budget), `founder-operating-system`.
- **Decision**: Zero mandatory login on Day-0. Candidates ingest their CV or test demo mandates immediately using a browser `localStorage` anonymous UUID. Account creation is prompted only when value is realized (e.g. claiming an inbound recruiter offer).
- **Alternatives Rejected**:
  - *Forced Google/LinkedIn Sign-in Wall on Landing*: Rejected because it creates an 85% drop-off barrier before the candidate experiences the gap scoring wedge.

## Decision 3: AI Output Paradigm — Typed Generative Cards with 1-Tap Checkboxes
- **Principle / Skill**: Intelligent UI (OpenAI GPT-6 reference), Law 6 (Three Depths Everywhere), `vercel-composition-patterns`.
- **Decision**: Model outputs typed tool invocations (`GapAnalysisCard`) instead of freeform prose. Renders 5 clear sections: Fatal Gaps, Skill-Up Path, Capstone Proofs, Honest Reframings, and Interview Shield.
- **Alternatives Rejected**:
  - *Static Markdown Bullet Lists*: Rejected because they cannot be toggled, audited, or interactively committed into the candidate's actual resume.

## Decision 4: LLM Model Selection & Authentication — Flagship Vertex AI Service Account
- **Principle / Skill**: Law 11 (Show Reasoning, Keep Control), Technical Reality Audit.
- **Decision**: Authenticate via Google Cloud Service Account with native IAM roles (`roles/aiplatform.user`) and default to Google's flagship reasoning model (`gemini-2.5-pro` on Vertex AI), with dynamic registry for frontier versions (`gemini-3.7-flash` / `gemini-3.8-flash`).
- **Alternatives Rejected**:
  - *Fragile API Keys / Secret Manager Hard Dependencies*: Rejected because missing secrets block automated Cloud Build releases and leak keys in config files.

## Decision 5: Layout & Perceptual Guardrails — Strict 3-Depth Disclosure & 44px Hit Targets
- **Principle / Skill**: `pencilplaybook`, `web-design-guidelines`, WCAG 2.2 AA.
- **Decision**: Glance (0-3s, $\le 3$ visual elements) $\rightarrow$ Act (3-10s, 1-tap diff/checkbox) $\rightarrow$ Learn (Non-blocking `<ProgressiveDrawer>` for dialectic debate & telemetry). Touch targets enforced at $\ge 44 \times 44\text{px}$.
- **Alternatives Rejected**:
  - *Inline Expandable Monoliths*: Rejected because long explanations blow out viewport height, ruining mobile thumb ergonomics.
