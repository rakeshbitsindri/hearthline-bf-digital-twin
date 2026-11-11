# Hearthline blast furnace advisory twin: single-image production build.
# One container serves the Next.js UI on $PORT and runs the FastAPI engine on an
# internal port. The Next server proxies /twin-api to FastAPI (see next.config.js),
# so the browser only ever talks to one origin. This matches Hugging Face Spaces
# (Docker SDK, app_port 7860), Render, Fly.io, and Google Cloud Run.

# ---- Stage 1: build the Next.js UI ----
FROM node:20-bookworm-slim AS web-build
WORKDIR /app/apps/web
COPY apps/web/package.json ./
RUN npm install
COPY apps/web/ ./
RUN npm run build

# ---- Stage 2: runtime with Python engine + Node server ----
FROM node:20-bookworm-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=7860 \
    TWIN_API_ORIGIN=http://127.0.0.1:8011

# Python for the FastAPI engine (numpy, pandas, scipy, scikit-learn, lightgbm).
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-venv libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv

# Install the Python engine dependencies into a venv.
COPY apps/api/requirements.txt /srv/apps/api/requirements.txt
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r /srv/apps/api/requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

# Copy the API source, the knowledge base, and the public reference dataset.
COPY apps/api /srv/apps/api
COPY data /srv/data
COPY knowledge /srv/knowledge
COPY CLAUDE.md ENTERPRISE_READINESS.md /srv/

# Copy the built Next.js app and its node runtime.
COPY --from=web-build /app/apps/web/.next /srv/apps/web/.next
COPY --from=web-build /app/apps/web/public /srv/apps/web/public
COPY --from=web-build /app/apps/web/node_modules /srv/apps/web/node_modules
COPY --from=web-build /app/apps/web/package.json /srv/apps/web/package.json
COPY --from=web-build /app/apps/web/next.config.js /srv/apps/web/next.config.js

COPY deploy/start.sh /srv/deploy/start.sh
RUN chmod +x /srv/deploy/start.sh

# Hugging Face Spaces and most PaaS hosts route to the single published port.
EXPOSE 7860
CMD ["/srv/deploy/start.sh"]
