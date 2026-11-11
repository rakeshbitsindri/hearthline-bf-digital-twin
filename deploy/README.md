# Deploying Hearthline for a free public showcase

The whole system (interactive twin UI, 3D cutaway, physics and ML engine, Golden Ranges, historical shortfall attribution, pitch deck) ships as one Docker image that listens on a single port. The browser only ever talks to that one origin, so there is nothing to wire up per host.

```
Browser  ->  Next.js UI ( $PORT )  ->  /twin-api proxy  ->  FastAPI engine (127.0.0.1:8011)
```

## Recommended free host: Hugging Face Spaces (Docker)

Best fit for this app. The free CPU Space gives 2 vCPU and 16 GB RAM, which comfortably runs pandas, scipy, scikit-learn, and lightgbm, and it gives a permanent public URL with no sleep surprises. No credit card.

1. Create a free account at huggingface.co.
2. Click New, then Space. Choose the Docker SDK, Blank template, CPU basic (free), visibility Public.
3. The Space is a git repo. Push this project into it:
   ```bash
   git clone https://huggingface.co/spaces/<your-username>/hearthline-bf-twin
   cd hearthline-bf-twin
   # copy the project contents in (Dockerfile, apps/, data/, knowledge/, deploy/, *.md)
   cp /root/Apps/BF_modeling/deploy/huggingface-space-README.md ./README.md
   git add .
   git commit -m "Hearthline blast furnace advisory twin"
   git push
   ```
4. The Space builds the Dockerfile and serves on port 7860 automatically. First build takes a few minutes. The public URL is `https://<your-username>-hearthline-bf-twin.hf.space`.
5. The app opens at `/`. The pitch deck is at `/pitch/`.

The `README.md` front matter in `deploy/huggingface-space-README.md` tells Spaces to use Docker and port 7860. It must be the README at the root of the Space repo.

## Alternative: Render (Docker web service)

Free, simple, but the free instance sleeps after 15 minutes idle and cold starts in under a minute, and the free tier has less memory, so the first model fit may be slow.

1. Push this repo to GitHub (a remote already exists).
2. At render.com, New, then Blueprint, and point it at the repo. Render reads `render.yaml`.
3. It builds the Dockerfile and publishes a public URL.

## Alternative: Fly.io

Generous always-on free allowance, a little more CLI work.

```bash
curl -L https://fly.io/install.sh | sh
fly launch --dockerfile Dockerfile --internal-port 7860 --now
```

## Run it locally with Docker first

Always smoke test the image before pushing to a host.

```bash
cd /root/Apps/BF_modeling
docker build -t hearthline .
docker run --rm -p 7860:7860 hearthline
# open http://localhost:7860  and  http://localhost:7860/pitch/
```

## Local development (no Docker)

```bash
# terminal 1: engine
cd apps/api && pip install -r requirements.txt && uvicorn main:app --port 8011
# terminal 2: UI
cd apps/web && npm install && npm run dev -- -p 3011 -H 0.0.0.0
# open http://localhost:3011
```

## Notes for a real customer deployment

This package is for a public, no cost showcase. Before any plant trial, see `ENTERPRISE_READINESS.md`: add authentication and SSO, put the audit store on PostgreSQL, terminate TLS, lock CORS to the plant origin, and run inside the OT and IT segmentation the site requires. None of that is enabled here on purpose, because the showcase is meant to be open and free to reach.
