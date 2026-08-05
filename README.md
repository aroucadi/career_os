# career_os — AI Career Intelligence & Job Strategy

A production-quality, modular knowledge base and multi-agent prompt repository for **CareerOS**, designed for deployment in **Claude Projects**.

## Repository Overview

```
CareerOS/
├── 00_CORE/                # Identity, Dispatcher, Intake, Communication & Reasoning Engine
├── 01_DECISION_TREES/      # Intent Classification, Input Matrix & Workflow Routers
├── 02_WORKFLOWS/           # Step-by-Step Execution Algorithms (Resume, ATS, Pivot, Interview, etc.)
├── 03_KNOWLEDGE_BASE/      # Domain Heuristics (ATS Mechanics, Recruiting, Market Dynamics, Comp)
├── 04_RUBRICS/             # Objective Scoring Models & Scorecards (/100 Composite, ATS, Recruiter)
├── 05_TEMPLATES/           # Output Formatting Blueprints (Resumes, Cover Letters, Outbound OS)
└── 06_PROMPT_COMPONENTS/   # Reusable Prompt Subroutines (Bullet Transformers, Action Verbs, STAR)
```

## Claude Project Deployment Instructions

1. **System Instructions**: Copy the contents of `00_CORE/CORE_Identity_Persona.md`, `00_CORE/CORE_Intent_Dispatcher.md`, and `00_CORE/CORE_Welcome_Protocol.md` into the **System Instructions** field of your Claude Project.
2. **Project Files**: Upload all remaining `.md` files directly as **Project Files** under your Claude Project knowledge base.
