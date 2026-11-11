# Blast furnace intelligence

A read-only advisory twin for blast furnace operating history. It checks a reduced-order furnace model against measurements, and it explains production shortfalls when the data can support that explanation.

This repository holds the domain research, the build prompts, and one public reference dataset. Application code starts after `prompts/00-kickoff-architecture.md` has been run and the design documents reviewed.

## Read first

| File | Why |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Rules for every session |
| [knowledge/README.md](knowledge/README.md) | Literature and model contracts |
| [knowledge/04-hidden-state-mechanisms.md](knowledge/04-hidden-state-mechanisms.md) | Why identical setpoints can still lose production |
| [data/public/evraz-zsmk-2013-2016/PROFILE.md](data/public/evraz-zsmk-2013-2016/PROFILE.md) | What the only open hourly series can and cannot support |
| [DATA_REQUEST.md](DATA_REQUEST.md) | What to ask the plant for |
| [prompts/README.md](prompts/README.md) | Order of implementation prompts |
| [PLAN.md](PLAN.md) | Build plan |

## Layout

```
CLAUDE.md
DATA_REQUEST.md
PLAN.md
knowledge/          literature and contracts
prompts/            one phase per file, 00 through 12
data/public/        EVRAZ ZSMK 2013–2016, CC BY 4.0
```

## Run the advisory twin

```bash
pip install -r apps/api/requirements.txt
cd apps/api && uvicorn main:app --port 8011
```

Ports 3000 and 8000 are often already taken on this machine. In another shell:

```bash
cd apps/web && npm install && npm run dev -- -p 3011 -H 0.0.0.0
```

Open `http://127.0.0.1:3011`. Tests: `cd apps/api && pytest`.

The browser only ever talks to the web port. `next.config.js` proxies `/twin-api/*` to the
API over loopback, so the app works unchanged on localhost, over a LAN address, or through a
single SSH tunnel. Point it at a different API with `TWIN_API_ORIGIN`, and bypass the proxy
entirely with `NEXT_PUBLIC_API` only if the browser can reach the API host directly.

Reaching it from another machine, either:

```bash
# one tunnel is enough; the API rides the same port
ssh -L 3011:127.0.0.1:3011 <user>@<server>   # then open http://127.0.0.1:3011
```

or browse `http://<server-address>:3011` directly if the port is reachable on your network.

The first silicon request fits a walk-forward LightGBM comparison and caches the card in `data/cache/`.

## Status

Design notes listed in `prompts/00-kickoff-architecture.md` are at the repository root. The API and command center run on the EVRAZ public file. A plant connector, full Rist balances, and commissioning sign-off stay blocked until plant data arrives.

The EVRAZ series is a public reference furnace. It is not this plant, and replaying it is not a live feed. Plant data, when it arrives, is a separate origin.
