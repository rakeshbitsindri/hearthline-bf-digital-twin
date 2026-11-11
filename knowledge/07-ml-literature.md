# What data-driven blast furnace models have actually achieved

Scope: hourly to cast-level data, a few hundred tags, forward prediction, anomaly detection, and setpoint recommendation. Accuracies above the bands in section 1 almost always come from a validation fault listed in section 6. Do not cite them as a target.

## 1. Silicon and hot metal temperature

Credible band after discarding weak validation: **RMSE 0.077–0.11 wt% Si**, hit rate **70–85% within ±0.1 wt%**, and **MAE 5–25 °C** on hot metal temperature at a 1–2 hour horizon.

| Work | Method | Data and split | Horizon | Reported accuracy |
|---|---|---|---|---|
| Tata Steel Port Talbot, Int J Adv Manuf Technol 2024 | Phased LSTM against CNN-LSTM, convolutional autoencoder, feedforward net | 4 years, 2.1 M minute rows, 219 columns, 19,723 casts. Walk-forward, 40 test blocks × 100 samples. | next cast | R² 0.71, MAE 0.123 %Si. [link](https://link.springer.com/article/10.1007/s00170-024-13214-6) |
| China Steel Tech Report 35 | LSTM vs XGBoost | 66 features from >2000. 1400 train / 700 test. | 2 h | RMSE 14.6 °C LSTM, 15.0 °C XGBoost. HMT variance −30% in production. [pdf](https://www.csc.com.tw/csc_e/ts/ena/pdf/no35/pages/14-The%20Comparison%20of%20LSTM%20and%20XGB%20Prediction%20Model%20of%20Hot%20Metal%20Temperature%20in%20the%20Blast%20Furnace.pdf) |
| China Steel Tech Report 33 | LSTM / GRU, DTW feature selection | 66 of 2600 features, critical lag ≤ 8 h | 2 h | MAE 25 °C LSTM, 20.5 °C GRU. [pdf](https://www.csc.com.tw/csc_e/ts/ena/pdf/no33/pages/14-Prediction%20Model%20of%20Blast%20Furnace%20Molten%20Iron%20Temperature%20Based%20on%20Time%20Series%20Data.pdf) |
| DCFANet, J. Sustain. Metall. 2025, Saxén group | Tuyere images plus GRU with attention | 4 months | 1–2 steps | MAE 5.45 °C, RMSE 7.28 °C. [doi](https://doi.org/10.1007/s40831-025-01042-1) |
| ENLR, ISIJ Int. 57(11) 2017 | Just-in-time ensemble local regression | industrial, 30 repeated splits | next tap | RMSE 0.077, hit rate 82.3%. Baselines JGPR / JLSSVR / ICA-JLSSVR at RMSE 0.097 / 0.098 / 0.093. [link](https://www.jstage.jst.go.jp/article/isijinternational/57/11/57_ISIJINT-2017-251/_html/-char/en) |
| JCSVR, Sensors 2017 | Just-in-time correntropy SVR | industrial, noisy | next tap | RMSE 0.079, hit rate 80.5%. Plain LSSVR was 0.141 / 52.5%. |
| Adaptive JLSSVR, ISIJ Int. 57(1) 2017 | JIT plus locality-preserving projection | a Chinese furnace | next tap | RMSE 0.086, hit rate 73.8%. |
| Bhattacharya, ISIJ Int. 45, 2005 | PLS, 6 latent variables | Tata G furnace, hourly, 120 predictors, 720 train / 24 test | 1 h and the day mean | Day-mean error 5.5%. Hourly skill decays after about 13 h. [doi](https://doi.org/10.2355/isijinternational.45.1943) |
| Saxén and Pettersson, IEEE TII 2012 | Review of discrete-time Si models | — | — | Canonical variable lists. [doi](https://doi.org/10.1109/tii.2012.2226897) |
| SHAP-Transformer, Iron & Steel 2025 | PCA windows, MIC lags, SHAP-weighted attention | 34 parameters reduced to 7 | next cast | Hit rate 72% within ±0.05, 96% within ±0.1. Directional agreement 87%. |
| GA-CNN-LSTM, ICCSMT 2025 | GA-tuned CNN-LSTM | 2500 m³ furnace | next cast | MAE 0.061 %Si. Hit rate 72% within ±0.05, 92% within ±0.1. |

**Numbers that do not survive.** An IEEE Access GBDT paper reports training R² of 0.993 for XGBoost and test R² barely above 0.4. On a second furnace the boosted models lose to a plain SVM ([doi 10.1109/access.2020.3034566](https://doi.org/10.1109/access.2020.3034566)). A Metallurgical Research & Technology claim of 98.77% for random forest replaced extreme outliers by interpolation across the whole series and then used random cross-validation. An MDPI *Materials* XGBoost pipeline (91% accuracy) used a random 85/15 split and random five-fold CV on about 1800 consecutive casts. The Port Talbot authors point out that a cited cluster-NARX network reaching R² 0.996 included silicon *at the prediction time* as an input.

**Rule.** Silicon is autocorrelated cast to cast. Report the persistence baseline — last cast's silicon, last hour's temperature — next to every model. A large fraction of published R² is persistence. DCFANet's 5.45 °C MAE is far below the 14–25 °C cluster and is one step ahead on densely sampled temperature, so read it as close to persistence plus trend unless a multi-hour horizon is shown separately.

## 2. Production and fuel rate

| Work | Method | Data | Target | Accuracy | Fault to remember |
|---|---|---|---|---|---|
| JSPL Angul 4554 m³, AIST 2022 | XGBoost plus MARS | Hourly, ~115 predictors, 4400 rows, 18 months of commissioning | Equivalent daily production, 8 h EMA | Cross-validated R² about 0.87. 13 terms, 8 variables, 4-way interactions. | The target is a two-sided 8-hour moving average. It contains the future. Not an online number. |
| Tata R&D, Steel Res Int 2024 | SVM, RF, XGB, then NSGA-II | 4 years daily, 1165 rows, 475 variables down to 9 manipulated | Production, fuel rate, Si, temperature | MAPE under 2% for production, fuel, temperature. Under 7% for Si. Hit rate above 80% for production and fuel, under 80% for Si and temperature. | Random 75/25 split of daily rows. |
| Sparrow-XGBoost, I&S 2024 | Tuned XGBoost | 652 samples | Utilisation factor | R² 0.76, MAPE 0.08 | Small sample. |
| ELM plus probabilistic reasoning, Chem Eng Trans 2022 | Extreme learning machine | 3.5 years, 94,875 records, 75 variables | Coke, PCI, fuel rate | RMSE 4.5 / 2.4 / 4.9 kg/t | Check the split before quoting. |
| Charcoal BF, Brazil, INFORMS 2021 | Ensemble plus sensitivity ranking | 9 years | Pig iron | Deployed. Ranking checked by process engineers. | Not a coke furnace. |

**Features that mattered at JSPL.** Permeability K was the top variable and acted as a pathway: other inputs reached production through it. Coke strength, ash, and moisture followed. Lime in sinter had an optimum, not a minimum. The best lookback was 8 hours, with skill falling sharply outside ±2 hours. That independently recovers the burden descent time.

**Features that mattered at Tata.** The top 20 for production, from an ensemble selection over 475 variables, included sinter, pellet, and coke-plant quality. Pre-ironmaking quality is not optional.

## 3. Permeability and abnormal conditions

| Work | Method | Claim | How to read it |
|---|---|---|---|
| TCN-GRU, ISIJ Int. 65(9) 2025 | LightGBM feature selection, VMD, then TCN-GRU, plus error compensation | Permeability 1 h ahead, RMSE 0.20, R² 0.965, 98% within ±0.5 | If VMD was fit on the whole series before the split, every mode contains the future. The paper must say it was fit inside the fold. |
| JFE Q-statistic, deployed | PCA SPE on shaft pressure and top-gas temperature | Channeling 2.5 h before the operator, on every JFE furnace | The most trustworthy result in this group. A linear statistic, a human baseline, a lead time. |
| TCN-BiGRU, ISIJ Int. 2025 | Body pressure and stockrod, with resampling | Upper hanging, 90.8% accuracy | Hanging is rare. Accuracy after oversampling is not precision at a fixed alarm budget. |
| TSIN, IEEE TII 2025 | Image-aligned time series | Channeling, hanging, slipping, collapse, 97% average | Same class-prior problem. |
| Two-stage PCA, ISIJ Int. 54(10) 2014 | T² and SPE, switching disturbances removed first | Direct PCA T² false-alarmed for 17.7 min. Two-stage SPE alarmed about 1.1 h earlier with the false alarms gone. | Multimode is mandatory. Stove switches, taphole rotation, and burden changes shift the mean. |
| Cluster VAE, Processes 2023 | Latent clustering | FAR 0.2%, no misses, against much worse PPCA baselines | Promising. Confirm the event definition. |
| 1-D convolutional autoencoder, Minerals 2021 | Reconstruction residual, blowback events | Lower delay and higher specificity than a dense autoencoder. Dynamic PCA had a lower delay and twice the failed predictions. | Report delay and specificity, not accuracy. |

## 4. Sample size

For lag-1 autocorrelation ρ, n_eff ≈ n · (1 − ρ) / (1 + ρ). At ρ = 0.8, 500 rows carry about 56 rows of information.

Three to four years of hourly data is 26,000–35,000 rows per furnace. Hot metal temperature, silicon, and permeability at hourly resolution will have lag-1 autocorrelation well above 0.9 if the thermal time constant is 8–12 hours. The honest count is the number of independent 8–12 hour blocks: roughly 2,500–4,000 per furnace, before campaign phase, season, and raw-material contract cut it further. Several furnaces multiply the count and add between-furnace heterogeneity. Model that hierarchy. Do not pool blindly.

JSPL said a full interaction model on their commissioning set would need billions of points and the data "is not powered". Feature reduction and regularisation are required, not optional.

## 5. Validation that matches deployment

Random splits put near-duplicates of a test row into training, because neighbouring hours share a state. The result is an optimistic error and intervals that are too narrow.

| Method | What it stops | What it costs |
|---|---|---|
| Contiguous blocked folds | Same-neighbourhood leakage | Fold scatter rises. That rise is the price of honesty. |
| Purging | Training rows whose label window overlaps a test label | About 1% of rows in a published worked example at a 10-step horizon. |
| Embargo after each test block | Features built from the target's own past (rolling means, lagged Si, lagged temperature) leaking the test block | An 8% embargo dropped about 9% of training rows in one study. Size it from the decorrelation lag, where ACF falls below about 2/√n. |
| Walk-forward | The actual deployment direction | Port Talbot used 40 test sets × 100 samples. Trains on less of the history. |

With purely exogenous features, purging was enough and the embargo bought nothing across embargo fractions of 0–8% ([purged CV study](https://purged-cv.marketmaker.cc/paper.pdf)). This feature set is not exogenous. Lagged silicon, lagged temperature, and rolling means are functions of the target's past. Use the embargo.

## 6. Leakage checklist, all of it seen in the BF papers above

- Interpolation or imputation fit on the whole series before the split.
- VMD, EMD, or wavelets fit on the whole series before the split.
- A two-sided moving-average target.
- A feature that is a descendant of the outcome (a later assay, a cast analysis used to predict that cast).
- Hyperparameters tuned on a random CV and then reported on the same split.
- Class rebalancing before the fold instead of inside it.
- Correlation screening, RFE, or lag search on the full dataset.
- No persistence baseline.

## 7. Hybrid models that have worked

Residual learning is the pattern with a result in ironmaking. Zhou and Saxén: an Aspen Plus mass-and-energy model makes a physically consistent and biased prediction, and a GRU with multi-head attention learns the residual. Four targets at once — silicon, slag basicity, top-gas CO utilisation, top-gas temperature — with hit rates above 90% inside stated margins ([Chem. Eng. Sci. 320(B) 122580, 2026](https://doi.org/10.1016/j.ces.2025.122580)).

JFE's three-way split is the one to copy:

- physical model for 8–12 hours, where the data-driven model has no skill,
- ML for 2–3 hours,
- a separate model of what the operator does, so the control policy is not mistaken for the plant.

Hashimoto's transient models with moving-horizon estimation update parameters against measured top-gas composition and absorb unmeasured disturbances such as ore iron content and coal carbon content ([ISIJ Int. 2019](https://doi.org/10.2355/isijinternational.isijint-2019-101)).

Use the physics model as the backbone and the learned model as the correction. Outside the training envelope the balance still closes. A pure ML model does not.

## 8. Uncertainty

| Method | Result | Source |
|---|---|---|
| Conformal prediction with a time-varying confidence split | 95.0% coverage and 6% narrower intervals on a wastewater series. 95.6% coverage and 16% narrower on a sintering series. | IEEE TII 2025 |
| Adaptive conformal under drift | Static split conformal and covariate-weighted conformal undercover the shifted regimes. Online ACI and rolling residual intervals recover the nominal coverage. | PMLR 2026, plant pH, train on one unit and test on four |
| Sliding-window conformal on a PLC soft sensor | Window 100: 95.3% coverage, wider. Window 40: 84.9%, narrower. | The trade is explicit. |
| Area of applicability | Flags a point outside the training predictor space. | Meyer and Pebesma 2021 |

Every prediction the product shows needs a point, an interval, a coverage statement, an in-envelope flag, and the model version. A bare number reads as a certainty the model does not have.

## 9. Optimisation results worth using as a ceiling

| System | What was optimised | Result |
|---|---|---|
| Tata, Steel Res Int 2024, NSGA-II | Max production, min fuel, Si and temperature constraints, 9 manipulated variables, bounds = historical ranges | Up to 5% on both, on the model. The bounds are a box, so they admit combinations that never occurred. Replace with a density or convex-hull envelope before believing the 5%. |
| JFE guidance, 2019 | Pulverised coal, NMPC | −1.9 °C variance, 70% operator approval, 2.5 °C setpoint reduction worth about 3 kg/t RAR |
| JFE automatic, 2022 | Same, closed | −4.6 °C mean error, −2.3 kg/t RAR |
| Kokura No. 2, 1977 | Oil injection | −15 °C, −4 kg/t |

Multi-objective Bayesian optimisation with a trust region (published on pressure-swing adsorption, transferable) reached a higher hypervolume than NSGA-II at about half the runtime and 20× fewer simulations, by refining locally and shrinking the radius when the gain stalled. Propagating surrogate uncertainty through the Pareto front moves the recommended point toward the conservative side. That conservative point is the one to show an operator.
