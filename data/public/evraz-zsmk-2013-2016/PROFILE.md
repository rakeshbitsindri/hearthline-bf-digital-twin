# Profile, computed 8 November 2026

Source files checked against `SHA256SUMS`.

## Coverage

- Hourly sheet: 29,602 rows, 2013-01-01 00:00 through 2016-05-18 09:00.
- Step is one hour for all 29,601 intervals. No duplicate timestamps. No nulls.
- Silicon sheet: 16,589 analyses, 2013-01-01 00:55 through 2016-05-11 08:50. Median spacing 1 hour 39 minutes. Maximum gap 12 days 14 hours.
- On-wind rule used here, blast flow above 1,000 m³/min: 28,032 hours (94.7%). Low-blast hours: 1,570 across 204 episodes. Blast flow is exactly zero for 280 hours. No delay code.

## Quality

Instrument spans are Table 3 of Trofimov, *Data in Brief* 63:112159. Hours outside those spans include negative pressures and gas readings, and a repeated sentinel near 3,311 °C on several thermocouples. Worst tag in that check is upper pressure drop, 784 hours (2.65%). Keep the rows. Mark the values bad.

On every hour, upper plus lower pressure drop matches total pressure drop within 0.01 kgf/cm² at the 95th percentile, and the median residual is zero.

## Signals that are real

Peripheral temperatures are uneven for the whole campaign. After clipping to 0–1,100 °C, median levels are about 405 °C and 391 °C on probes 4 and 5, and about 188–204 °C on probes 8–10. Median circumferential range is 269 °C. In 91.9% of on-wind hours the range exceeds 150 °C. The four top temperatures have median range 29 °C, and only 4.1% exceed 100 °C. The pattern is azimuthal, not a single failed top-gas measurement.

Silicon mean is 0.49 wt%. Persistence RMSE, previous cast to next cast, is 0.120 wt%. Lag-1 autocorrelation is 0.74, so the effective sample count is about 2,500. Hourly hot-blast temperature on wind has lag-1 autocorrelation 0.96.

Correlations of blast, oxygen, temperature, pressure drop, CO₂, hydrogen, and ore-to-coke ratio with silicon are negative and nearly flat from a same-hour match through a 24-hour lag. Correlations of four-hour changes in those inputs with the next silicon change are about −0.05 to 0.03. Do not read a setpoint from the level correlation.

## Fit

Use this file for ingestion, clocks, units, bad-value classification, the pressure-drop identity, a circumferential display, silicon forecasts that must beat 0.120 wt% RMSE, and a replay stream whose clock stays in 2013–2016.

Do not use it for tonnes, a mass or heat balance, PCI, a separate coke rate, hearth level, alkali inventory, a dimensioned 3D furnace, or an inverse recommendation. Those features stay `not_testable` or `not_observable` until a plant extract supplies the inputs in `knowledge/13-parameter-tiers.md`.

The 127 condition labels can be shown as named examples. They are too few, and too evenly spread across classes, to be a classifier training set.
