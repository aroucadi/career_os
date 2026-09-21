# ==========================================
# Stage 1: Frontend Next.js Standalone Build
# ==========================================
FROM node:20-bookworm-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# ==========================================
# Stage 2: Production Unified Cloud Container
# ==========================================
FROM python:3.13-slim-bookworm AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8080 \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system utilities, Node.js, and font libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    nodejs \
    npm \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -fv

WORKDIR /app

# Install Python backend dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browser and its required system libraries
RUN python -m playwright install --with-deps chromium || true

# Copy Backend Python codebase
COPY 00_CORE/ 00_CORE/
COPY 01_DECISION_TREES/ 01_DECISION_TREES/
COPY 02_WORKFLOWS/ 02_WORKFLOWS/
COPY 03_KNOWLEDGE_BASE/ 03_KNOWLEDGE_BASE/
COPY 04_RUBRICS/ 04_RUBRICS/
COPY 05_TEMPLATES/ 05_TEMPLATES/
COPY 06_PROMPT_COMPONENTS/ 06_PROMPT_COMPONENTS/
COPY 07_TARGET_JDS/ 07_TARGET_JDS/
COPY api/ api/
COPY career_radar/ career_radar/
COPY engine/ engine/
COPY evals/ evals/
COPY profiles/ profiles/
COPY resumes/ resumes/
COPY storage/ storage/
COPY careeros_cli.py ./

# Copy Frontend Standalone assets from Stage 1
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend-server
COPY --from=frontend-builder /app/frontend/.next/static ./frontend-server/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend-server/public

# Copy Entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT:-8080}/api/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
