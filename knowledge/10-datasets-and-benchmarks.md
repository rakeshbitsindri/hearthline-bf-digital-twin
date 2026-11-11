# Public datasets and the leakage benchmark

No public dataset is a multi-year, hourly, several-hundred-tag, multi-furnace blast furnace record. Every industrial accuracy in [07-ml-literature.md](07-ml-literature.md) sits on proprietary data, which is why cross-paper comparison is weak. The Port Talbot authors say this themselves.

The one open hourly blast-furnace sensor file is already stored in `data/public/evraz-zsmk-2013-2016/`. It is EVRAZ ZSMK, 2013–2016, 29,602 hours, CC BY 4.0. Read `PROFILE.md` before treating it as a twin. It does not include production, PCI, or a separate coke rate. Papers that describe Tata, JSPL, SAIL, Baosteel, and US furnace extracts do not attach the files.

Use the sets below to prove the pipeline before plant data arrives. A method that cannot recover the known answers here does not get pointed at the furnace.

## 1. Iron-ore flotation — causal ground truth

**Quality Prediction in a Mining Process**, Magalhães 2017. A Brazilian reverse-cationic flotation plant, March–September 2017. 737,453 rows, 24 columns. Process tags at 20 seconds. Feed and concentrate assays hourly from the lab. Target is percent silica in the iron concentrate. About 184 MB.

[Kaggle](https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process).

This is the closest public analogue to the intended system: fast process tags, a slow lab target, operators dosing reagents in closed loop, one long record.

The published causal analysis of this exact record ([09-confounding-and-causality.md](09-confounding-and-causality.md)) is the acceptance test:

| Claim the code must recover | Value |
|---|---|
| Pulp pH effect on concentrate silica | about −0.08 to −0.10 percentage points per the interventional estimators, interval excludes zero |
| Gradient-boosted partial dependence on pH | near zero, interval includes zero — and this disagreement must be reported, not averaged away |
| Amine collector | not identifiable |
| Aeration | largest identified effect, carried by one column, gone in the bank mean |
| Concentrate iron assay as a feature | lifts R² from about 0.36 to 0.78 and is leakage, because it is a descendant of the outcome |
| Block length | 24 hours |

## 2. Tennessee Eastman — detection delay ground truth

Rieth et al. 2017. Four R files: fault-free and faulty, training and testing. 500 runs each, 55 columns, 3-minute sampling. Training runs are 25 hours, test runs 48 hours. Faults 1–20 plus fault-free. Faults start at exactly 1 hour in the training runs and exactly 8 hours in the test runs. About 1.3 GB. Public domain.

[Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/6C3JR1). CSV mirror on Kaggle as `tep-csv`.

Use it to measure detection delay and false-alarm rate against a known onset. The lag-specific transfer entropy paper and the causal-discovery comparisons also use this process, so there is a published number to sit next to yours. Do not claim a blast furnace false-alarm rate until this benchmark has been run and written down.

## 3. The one public blast furnace extract

`ironmaking-zju` (GitHub `ylkyc/ironmaking-zju`). Raw data and code for *A Survey of Data-Driven Soft Sensing in Ironmaking System*. Real blast furnace and sinter data from a plant in south China, released with permission. Soft-sensing targets around silicon and molten-iron quality. Research use only, no commercial use.

[github.com/ylkyc/ironmaking-zju](https://github.com/ylkyc/ironmaking-zju).

Small relative to a four-year hourly extract. It is still the only public place to test blast-furnace feature engineering on real furnace signals. Read the licence before copying it into this repo. Do not redistribute it.

## 4. Steel-plant energy, for the validation machinery

DAEWOO Steel, Gwangyang. 35,040 rows, 15-minute resolution, one year. Energy, reactive power, CO₂, load type, weekday. UCI dataset 851, also mirrored on Kaggle.

[UCI](https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption).

Not blast furnace physics. Useful for seasonality, regime labels, and blocked cross-validation on a real 15-minute industrial series that fits in memory.

## 5. Synthetic furnace, once Phase 1 exists

The perturbed generator specified in `../prompts/04-phase4-dynamic-twin.md` is a separate implementation from the twin. It proves the software under mismatch, noise, and missing tags. It does not prove metallurgical accuracy. Every screen that shows synthetic output carries a visible synthetic-data marker. The EVRAZ files are public reference measurements, not synthetic.

## 6. Order of proof

1. Flotation causal test passes (section 1).
2. Tennessee Eastman delay and false-alarm numbers are written down (section 2).
3. Walk-forward validation, persistence baseline, and conformal coverage pass on the synthetic furnace, including the seeded hidden-state case where the mean-only model must fail and the mystery protocol must name the seeded cause.
4. Only then point the same code at plant data, and publish a capability report that restates what failed.
