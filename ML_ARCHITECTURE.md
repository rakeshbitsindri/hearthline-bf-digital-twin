# Prediction

Target: next cast silicon. Features known at the cast: previous silicon, and blast, oxygen flow, hot-blast temperature, total pressure drop, CO₂, H₂, and ore-to-coke ratio from the previous hour.

Validation: five contiguous walk-forward blocks. Embargo of 24 casts between train and test. Metrics: RMSE and MAE. Persistence is the previous cast. LightGBM is the second model, with a small tree count. The served model is the one with the lower mean test RMSE. Both numbers are stored on the model card from the run.

No random split. No same-cast silicon as an input. The decision model is not served, because the EVRAZ change-correlations do not identify a blast effect.
