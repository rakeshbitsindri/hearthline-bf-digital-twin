# 07 — Anomaly detection and sensitivity

Read `knowledge/05-failure-mode-catalog.md`, section 3 of `knowledge/07-ml-literature.md`, and `knowledge/10-datasets-and-benchmarks.md`.

## Build

1. Residuals from phase 5 when a model exists. Otherwise a robust baseline fit only on the past.

2. EWMA and CUSUM on residuals. An alarm requires persistence across a configured number of hours. Shewhart beside them for large spikes. Store alarm count.

3. PCA Q-statistic on the distributed temperature or pressure matrix after removing labelled switches. On EVRAZ the peripheral temperatures are the matrix. A single global model is a comparison that should show extra alarms, then be rejected if the split model is better.

4. Change-point on silicon and on pressure drop.

5. Contextual sensitivity: band, short and long variance, and the lagged association with the available target. Label it associational. A 1% move is scored by that association.

6. React Flow graph of significant lag associations. Caption: hypothesis, not a causal graph.

7. Tennessee Eastman benchmark. Write `docs/te-benchmark.md` with detection delay and false-alarm rate before any furnace detection-rate sentence.

## UI

Alarm list with start, end, statistic, and contributing tags. Opening an alarm shows the residual and the data age. EVRAZ alarms are labelled 2013–2016.

## Exit tests

- A synthetic bias in one peripheral probe raises the Q-statistic without a Shewhart alarm on the average of the other probes.
- A spike shorter than the persistence window does not alarm.
- The TE document exists and the test reads its numbers.
