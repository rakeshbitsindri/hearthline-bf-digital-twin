# API

| Method | Path | Returns |
|---|---|---|
| GET | /health | status, origin |
| GET | /furnace | identity, assumed geometry, timezone note |
| GET | /capability | feature statuses from the cache build |
| GET | /series | tag, from, to, values, evidence |
| GET | /quality | instrument-range violation counts |
| GET | /physics/pressure | identity residual for the selected hour |
| GET | /physics/utilisation | not_run on this file |
| GET | /predict/silicon | served model, interval, card |
| GET | /diagnose | gate list |
| GET | /twin | filtered tags at t, hidden states |
| POST | /scenario | blast delta, labelled scenario |
| GET | /model-card | walk-forward metrics |
| POST | /audit | append-only accept or reject |
| POST | /connector/probe | read accepted, write rejected |

No route writes a plant tag.
