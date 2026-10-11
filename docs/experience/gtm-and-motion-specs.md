# CareerOS: Go-to-Market (GTM), Motion & Design Specifications

## 1. Core Principles: Replacing Adjectives with Specifications

In accordance with our gStack and Design System protocol, every adjective describing the product experience has been codified into exact technical values:

```
Adjective                -> Specification
"Instant response"       -> <= 120ms tactile feedback; <= 2000ms end-to-end rescore
"Restrained animation"   -> Damping ratio zeta = 0.82; 120ms feedback; 350ms move; 180ms exit
"Zero layout jump"       -> Cumulative Layout Shift CLS = 0.000; font-variant-numeric: tabular-nums
"Trustworthy data"       -> Verbatim substring extraction from CV; zero hallucinated credentials
"Accessible controls"    -> Touch targets >= 44x44px; WCAG AA contrast ratio >= 4.5:1
```

---

## 2. Motion Token Architecture (Globals & Primitives)

Integrated directly into `frontend/app/globals.css`:

```css
/* Layer 3: Motion Tokens */
--ease-enter: cubic-bezier(0.22, 1, 0.36, 1); /* ease-out-quint */
--ease-exit: cubic-bezier(0.7, 0, 0.84, 0);   /* ease-in-expo */
--ease-move: cubic-bezier(0.76, 0, 0.24, 1);  /* ease-in-out-quart */
--ms-feedback: 120ms;                         /* button press, toggle */
--ms-move: 350ms;                             /* drawer slide, tab switch */
--ms-hero: 750ms;                             /* hero card presentation */
--ms-exit: 180ms;                             /* dismissals (40-50% shorter) */
--stagger-item: 50ms;                         /* list item entrance */
```

### Motion Guardrails
1. **The Rule of Holds**: Text is **never** moved or scaled while being read. Content remains static; only the container's entrance/exit is animated.
2. **Transform & Opacity Only**: No animation on `width`, `height`, `top`, or `left` to protect the browser render thread from layout recalculation.
3. **Respect Reduced Motion**: `prefers-reduced-motion: reduce` completely disables transitions across all interactive elements.

---

## 3. Go-to-Market (GTM) Strategy & Positioning

### 3.1 The Silicon Valley Positioning Formula
> **For** senior engineering leaders, architects, and freelance consultants  
> **Who** struggle with opaque ATS algorithms and recruiter screening traps,  
> **CareerOS** is an autonomous AI career intelligence workspace  
> **That** quantifies job-to-resume skill gaps and writes truth-grounded bullet upgrades in under 10 seconds.  
> **Unlike** generic ChatGPT prompt dumps or hallucinated resume tools,  
> **CareerOS** mathematically anchors every suggestion to verified candidate history with zero hallucinated fluff.

### 3.2 The First Three Seconds (Landing Page & Social Video)
Audiences in 2026 demand **demonstration over claims**. Our launch media follows the strict 15-second beat grid:

```text
[00:00 - 00:03] HOOK: Screen opens on candidate CV showing 58% Match Fit with 2 fatal gaps in red.
[00:03 - 00:08] DEMO: User taps 1 checkbox on the Intelligent UI Card -> Score ticks to 88% (+30 pts).
[00:08 - 00:12] PROOF: Truth Guard badge verifies: "Derived from candidate CV sentence #14. Zero hallucinations."
[00:12 - 00:15] CTA: "Audit your target mandate anonymously at careeros-365518648716.europe-west1.run.app"
```

---

## 4. Production Launch QA Checklist (Passed)

- [x] **Goal of each screen written in one sentence**: Mandate Stream answers *"Where do I stand against my target role today, and what is my highest-leverage move?"*
- [x] **Hierarchy**: Exactly 1 hero metric (`Match Score`), $\le 3$ visual groups per card, 1 dominant action.
- [x] **All states designed**: Empty, loading skeleton, error fallback, verified success state.
- [x] **Tokens only**: No hardcoded hex values or raw duration integers in component code.
- [x] **Contrast & Accessibility**: $\ge 4.5:1$ contrast ratio for body text; $\ge 44 \times 44\text{px}$ touch targets.
- [x] **Motion compliance**: Entrances `ease-out-quint`, exits `ease-in-expo` ($180\text{ms}$), spring damping $\zeta = 0.82$.
