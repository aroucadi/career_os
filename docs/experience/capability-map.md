# CareerOS Capability Map & Ideal-Flow Architecture

## 1. Capability Registry

| Capability | Promise (One Sentence) | Moments Contributed to Anchor | Emits Signals | Consumes Signals | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mandate Matcher & Gap Radar** | Reveal exact ATS score & missing competencies against target roles in seconds. | First JD analysis, daily market scan | `gap_detected`, `score_computed` | `cv_uploaded`, `track_changed` | **ACTIVE (Built)** |
| **Grounded Bullet Tailor** | Upgrade resume bullets using Google XYZ format grounded exclusively in candidate facts. | Low match score warning, application preparation | `bullets_optimized`, `diff_committed` | `gap_detected`, `user_checkbox_toggle` | **ACTIVE (Built)** |
| **Dialectic Mandate Evaluator** | Run adversarial debate (Prosecutor vs Advocate) on role risks and compensation leverage. | Offer received, mandate shortlisted | `verdict_rendered`, `leverage_scored` | `jd_selected` | **ACTIVE (Built)** |
| **Anonymous Talent Graph** | Match candidate anonymously with vetted employers based on verified skills. | Inbound interview requests, compensation bids | `inbound_offer_received` | `bullets_optimized`, `score_computed` | **ACTIVE (Built)** |
| **Market Compensation Oracle** | Dynamic day-rate & base salary telemetry based on live European tech filings. | Rate negotiation, career track switch | `benchmark_calibrated` | `track_changed` | **LOCKED (Roadmap v3)** |

---

## 2. Ideal User Flow

| Trigger / Context | Moment | Capability | Primary Action (Budgeted) | Cross-Capability Value |
| :--- | :--- | :--- | :--- | :--- |
| **User lands anonymously** | Blank Slate Evaluation | Gap Radar | 1-tap test run (`/gap` or `/evaluate JD_34`) | Instant score without registration |
| **User uploads CV** | Ground Truth Ingestion | Parser & Embedder | Upload drag-and-drop ($\le 10\text{s}$) | Career skills graph extracted into localStorage |
| **Gap identified** | Tactical Remediation | Bullet Tailor | 1-tap checkbox toggle & rescore ($\le 2$ taps) | Bullet diff upgrades candidate ATS score live |
| **Job shortlisted** | Adversarial Verification | Dialectic Evaluator | Inspect prosecutor traps in Drawer ($\le 2$ taps) | Uncovers hidden equity / tech stack liabilities |
| **Inbound Recruiter match** | Private Opportunity | Anonymous Graph | Accept/Decline recruiter inquiry ($\le 1$ tap) | PII remains encrypted until candidate consents |

---

## 3. Extensibility Contract (Code & Architecture)

```typescript
export interface Moment {
  id: string;
  capability: string;
  trigger: 'time' | 'state' | 'command';
  title: string;
  glance: {
    eyebrow: string;
    metric?: string;
    headline: string;
  };
  primaryAction: {
    label: string;
    actionId: string;
    targetPayload: any;
  };
  learnDrawer?: {
    title: string;
    component: string;
  };
  status: 'active' | 'completed' | 'dismissed';
}

export interface Signal {
  capability: string;
  type: string;
  value: Record<string, any>;
  timestamp: string;
}

export interface UIIntent {
  id: string;
  component: 'SurfaceCard' | 'GenerativeCard' | 'InteractiveCheckin' | 'ProgressiveDrawer';
  props: Record<string, any>;
  source: 'rule' | 'model';
  fallbackText: string;
}
```
