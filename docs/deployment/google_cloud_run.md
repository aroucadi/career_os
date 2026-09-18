# ☁️ Google Cloud Run & Gemini LLM Deployment Guide

**Target Product**: CareerOS 2.0  
**Target Infrastructure**: Google Cloud Platform (Google Cloud Run + Artifact Registry + Secret Manager)  
**Cognitive Engine**: Google Gemini LLM (`gemini-3.7-flash` / `gemini-2.5-flash` / `gemini-2.5-pro`)

---

## 1. Architectural Overview

CareerOS 2.0 is containerized as a unified, high-performance production workload on **Google Cloud Run**:
- **Frontend Layer**: Next.js 14.2 App Router compiled with `output: "standalone"` into an ultra-lean static & SSR Node server.
- **Backend Layer**: FastAPI running Python 3.13, managing SQLite WAL persistence, Dialectic Debates, and Double Opt-In matching.
- **Reverse Proxy**: Native internal loopback — Next.js serves on Cloud Run's `$PORT` (8080) and seamlessly reverse-proxies `/api/*` to FastAPI on `127.0.0.1:8000`.
- **Reasoning Layer**: Direct low-latency calls to Google Gemini via Google's OpenAI-compatible REST endpoints or `google-genai` SDK.

```
                  ┌────────────────────────────────────────┐
                  │          Cloud Run (Port 8080)         │
                  │                                        │
 Incoming ───────►│  Next.js Standalone (Port 8080)        │
 Traffic          │    ├── Static Assets & UI App Router   │
                  │    └── Rewrites /api/* ────────┐       │
                  │                                │       │
                  │  FastAPI Backend (Port 8000) ◄─┘       │
                  │    ├── SQLite WAL Database             │
                  │    ├── Dialectic Audit & A4 Compiler   │
                  │    └── LLM Client (Gemini 3.7 Flash)   │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                     Google Generative Language API
                         (Gemini 3.7 Flash / Pro)
```

---

## 2. Prerequisites

1. **Google Cloud SDK (`gcloud`)** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
2. Enable required Google Cloud APIs:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com \
     secretmanager.googleapis.com
   ```

---

## 3. Configure Secrets in Google Secret Manager

Store sensitive keys securely in Secret Manager so they are injected directly as environment variables in Cloud Run:

```bash
# 1. Google Gemini API Key
echo -n "AIzaSy..." | gcloud secrets create GEMINI_API_KEY --data-file=-

# 2. CareerOS Platform Secret Key
echo -n "your-secure-random-64-char-hex-secret" | gcloud secrets create CAREEROS_SECRET_KEY --data-file=-

# 3. Stripe Secret Key (Recruiter Billing)
echo -n "sk_live_..." | gcloud secrets create STRIPE_SECRET_KEY --data-file=-

# 4. Resend API Key (Double Opt-In Email Notifications)
echo -n "re_..." | gcloud secrets create RESEND_API_KEY --data-file=-
```

Grant Cloud Run's service account permission to access these secrets:
```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding CAREEROS_SECRET_KEY \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 4. Setup Google Artifact Registry

Create an Artifact Registry Docker repository:

```bash
gcloud artifacts repositories create careeros-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --description="CareerOS Production Container Repository"
```

---

## 5. One-Click Automated Deployment via Cloud Build

Submit the build and deployment pipeline directly using the bundled `cloudbuild.yaml`:

```bash
gcloud builds submit --config cloudbuild.yaml
```

This single command:
1. Builds the multi-stage production container with BuildKit caching.
2. Pushes `europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/careeros-repo/careeros:latest`.
3. Deploys to Cloud Run with 2 CPUs, 2GiB RAM, auto-scaling from 0 to 10 instances, and bound Secret Manager keys.

---

## 6. Manual Deployment (Direct gcloud Command)

Alternatively, build locally and deploy directly:

```bash
# Build & tag image
docker build -t europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/careeros-repo/careeros:latest .

# Configure Docker for Artifact Registry
gcloud auth configure-docker europe-west1-docker.pkg.dev

# Push image
docker push europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/careeros-repo/careeros:latest

# Deploy to Cloud Run
gcloud run deploy careeros \
  --image europe-west1-docker.pkg.dev/YOUR_PROJECT_ID/careeros-repo/careeros:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars DEFAULT_MODEL=gemini-3.7-flash,NODE_ENV=production \
  --set-secrets "GEMINI_API_KEY=GEMINI_API_KEY:latest,CAREEROS_SECRET_KEY=CAREEROS_SECRET_KEY:latest"
```

---

## 7. Local Cloud Run Verification (Docker Compose)

Before deploying to Google Cloud, test the identical container locally:

```bash
# 1. Populate your test Gemini key
export GEMINI_API_KEY="AIzaSy..."

# 2. Launch container with docker-compose
docker compose -f docker-compose.cloud.yml up --build

# 3. Test health check
curl http://localhost:8080/api/health
```

Navigate to `http://localhost:8080` in your browser to verify the Next.js UI, dialectic streaming, and Gemini reasoning.
