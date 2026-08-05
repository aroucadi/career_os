# WF: Industry Opportunity Scanner Workflow

## Purpose
Scans and ranks target economic sectors by hiring demand, compensation levels, remote availability, and AI disruption risk.

---

## Step-by-Step Execution Protocol

1. **Sector Data Retrieval**: Query domain knowledge files under `03_KNOWLEDGE_BASE/MARKET/*`.
2. **Multi-Vector Industry Evaluation**: Score candidate target industries across 6 parameters:
   - **Hiring Demand Volume** (High / Med / Low).
   - **Compensation Bands** ($ Tier).
   - **Remote / Hybrid Share** (%).
   - **AI Disruption Vulnerability Index** (Low Risk / High Augmentation / High Displacement).
   - **Barrier to Entry** (Low / Med / High).
   - **5-Year Growth Outlook**.
3. **Ranked Opportunity Matrix Output**: Deliver a comparative ranking table highlighting top candidate target sectors.

---

## Related Files & Dependencies
- **Labor Market Dynamics**: `03_KNOWLEDGE_BASE/MARKET/KNOW_Labor_Market_Dynamics.md`
- **AI Disruption Index**: `03_KNOWLEDGE_BASE/MARKET/KNOW_AI_Disruption_Index.md`
