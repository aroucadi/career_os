# 🚀 CareerOS Sprint 1 Execution Plan, Ship Gate & Kill Triggers

> **Document Status**: Production Strategy Spec  
> **Author**: Silicon Valley Head of Product & YC Advisory  
> **Frameworks Applied**: `gstack-review`, `gstack-qa`, `startup-kill-switch`  
> **Release Target**: Sprint 1 "Unbeatable Wedge"  

---

## 🎯 1. SPRINT 1 SCOPE: THE UNBEATABLE WEDGE

Zero fluff, zero B2B recruiter tools, zero avatar interview bots. Only the 4 essential engines:

```
[Candidate Landing]
       │
       ▼
1. Zero-Friction Ingestion  ───► Drag-drop CV (PDF/MD) + Paste 1 JD URL/Text
       │
       ▼
2. Diagnostic Gap Engine    ───► Recruiter Score (0-100%) + 3 Fatal ATS Gaps (<30s)
       │
       ▼
3. Surgical Diff Tailor     ───► Side-by-side honest bullet rewriting + 1-Click Export
       │
       ▼
4. Screening Cheat-Sheet    ───► 5 targeted technical questions addressing gaps
```

---

## 🚦 2. SHIP GATES & VERIFICATION CRITERIA

Before merging to main or releasing to alpha users:

### A. Experience & Performance Quality Gates
- [ ] **TTV Budget $\le 45$ Seconds**: From the landing page to the rendered Diagnostic Score must take under 45 seconds total (including LLM processing).
- [ ] **Tap/Click Ceiling $\le 2$ Clicks**:
  - Click 1: Submit CV + JD.
  - Click 2: Export Tailored Resume Diff.
- [ ] **Zero Cumulative Layout Shift (CLS = 0)**: Diagnostic results must render into reserved card containers or skeleton loaders; no jumping buttons as async LLM streams arrive.
- [ ] **Mobile Responsive (390px Viewport)**: Fully verified on mobile viewports with minimum 44×44px touch targets.

### B. LLM Truth & Hallucination Guard
- [ ] **Zero Hallucination Tolerance**: The tailoring engine MUST NEVER invent degrees, certifications, companies, or programming languages the candidate did not include in their original CV. It may only re-frame and emphasize real accomplishments.

---

## ☠️ 3. STARTUP KILL-SWITCH TRIGGERS (14-DAY POST-LAUNCH AUDIT)

Per [`startup-kill-switch`](file:///C:/Users/rouca/.gemini/config/skills/startup-kill-switch/SKILL.md), if these thresholds are not met after **14 days of live testing with 50 candidates**, the feature or direction is **killed immediately**:

| Check | Failure Threshold | Prescribed Founder Action |
| :--- | :--- | :--- |
| **Activation Rate** | $< 40\%$ of uploaders view diagnostic | Kill current onboarding UI; replace with 1-input text paste. |
| **Value Conversion** | $< 10\%$ export tailored CV | Kill current prompt templates; conduct 5 manual teardowns to rewrite prompts. |
| **Day 7 Repeat Rate** | $< 15\%$ return for 2nd application | The core loop is broken; candidate found no utility. Pause all coding. |
| **Paid Conversion** | 0 paid sprint passes sold | **KILL RECURRING SUBSCRIPTION PLAN**. Switch exclusively to \$49 manual concierge teardowns. |

---

## 🗓️ 4. SPRINT 1 IMMEDIATE MILESTONES

1. **Day 1**: Strip out legacy multi-role recruiter/headhunter concepts from prompts and codebase.
2. **Day 2**: Harden the fast CV+JD Diagnostic API route (`/api/diagnostic`) with deterministic JSON schemas.
3. **Day 3**: Implement the 3-depth UI (Glance → Act → Deep-Dive) on the web dashboard.
4. **Day 4**: Integrate Stripe checkout for the \$19 Sprint Pass and \$39 Pro Sprint.
5. **Day 5**: Manual outreach to 10 senior tech candidates on LinkedIn/X to run live concierge sessions.
