# Connector

The web process has no historian client. `POST /connector/write` does not exist. `POST /connector/probe` accepts only `{ "op": "read" }` and rejects `write`, `method`, and `query`.

A future adapter may read a named view on a DMZ replica. Secrets stay in the environment, never in the repo. This build does not open a socket to a plant.
