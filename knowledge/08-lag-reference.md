# Time lags and active rates

A blast furnace snapshot mixes several pasts. Blast acts within about an hour. The coke now in front of the tuyeres was charged 5–8 hours ago. Hot metal temperature still carries more than 8 hours of thermal memory. Comparing two hours on instantaneous setpoints, without shifting each input by its own lag, will call different furnaces "the same".

Lags are furnace-specific, production-rate dependent, and sometimes bimodal. Estimate them. Do not hardcode one lag for every tag.

## 1. Published delays

| Input or process | Output | Delay | Source |
|---|---|---|---|
| Blast volume, temperature, oxygen | Metallurgically active | within about 1 hour | Primetals VAiron description, IntechOpen expert-system chapter |
| PCI / injected coal rate | Active in the furnace | 1.5–3 hours | same |
| Charged coke rate | Active at the tuyeres | 5–8 hours | same |
| Burden descent, stockline to hearth | Hot metal produced | about 6 hours commonly quoted; about 4 hours in one teaching model; 6–8 hours in China Steel notes | [ISIJ Int. 59(9) 1573](https://www.jstage.jst.go.jp/article/isijinternational/59/9/59_ISIJINT-2019-119/_pdf), CSC Tech Report 33 |
| Hot metal temperature | Overall thermal response | time constant above 8 hours; one study quotes about 12 hours of heat capacity | ISIJ Int. 2019; TU Delft / Hashimoto notes |
| Coke-ratio step | Hot metal temperature | about 6 hours, equal to burden descent | [ISIJ Int. 2019-101](https://doi.org/10.2355/isijinternational.isijint-2019-101) |
| Blast moisture step | Hot metal temperature | fast: minutes to tens of minutes | same |
| Pulverised coal step | Hot metal temperature | slower than moisture | same |
| Blast humidity | Pig iron temperature | 110 minutes (lag 22 at 5-minute sampling) | [Sensors 2025, lag-specific transfer entropy](https://www.mdpi.com/1424-8220/25/13/3980) |
| Blast temperature | Pig iron temperature | 115 minutes | same |
| Pulverised coal ratio | Pig iron temperature | bimodal: 10 minutes (hydrocarbon decomposition) and 235 minutes (gas ascent and reduction) | same |
| All inputs | Hourly production | 8 hour lookback was optimal; skill fell sharply outside ±2 hours of 8 | [AIST Digital Transformations, March 2022, JSPL Angul](https://www.aist.org/AIST/aist/AIST/Publications/Digital%20Transformations/22_Mar_036_045_dig_trans.pdf) |
| Physical model vs ML model | Hot metal temperature horizon | physical model useful 8–12 hours ahead; ML model 2–3 hours ahead | [JFE guidance product page](https://www.jfe-steel.co.jp/en/products/solution/data-science/14-control-guidance.html) |
| Hearth control actions | Deadman / hearth response | four weeks or more | Kobe Steel centre-coke practice |
| HM sulphur, shifted | Hearth sump depth | about 4 weeks lead | Åbo Akademi hearth wear study |
| Sinter quality change | Full expression in wall heat load and channeling | about 2 weeks in the thyssenkrupp ore-change case | SEAISI / SIP paper |
| Alkali and zinc inventory | Permeability and coke rate | days to weeks to accumulate; weeks to flush | dissection literature, see [04-hidden-state-mechanisms.md](04-hidden-state-mechanisms.md) |

Nippon Steel has noted that local linear models are enough inside about 4 hours and that nonlinear models are needed beyond 4 hours ([NSC report 123-15](https://www.nipponsteel.com/en/tech/report/pdf/123-15.pdf)).

## 2. Active rate, not the setpoint

Primetals' VAiron does not feed the instantaneous coke rate into its thermal calculation. It sums coke changes over the last 5–8 hours and coal changes over the last 1.5–3 hours, and calls the result the *active* rate. Copy that idea.

For each manipulated variable, store:

- the instantaneous value,
- the active value over its estimated lag window,
- the change over that window,
- the value that was charged or set one residence time ago.

Two hours with the same blast volume and the same coke setpoint can have different active coke if the charging rate moved six hours earlier.

## 3. How to estimate lags

Use more than one method and keep a lag only when they agree, or when a process engineer confirms it.

1. Cross-correlation and the maximal information coefficient inside a sliding window.
2. Lag-specific transfer entropy with a self-prediction step that removes each sensor's own information storage, plus time-shifted surrogate tests. This has been run on a full-scale blast furnace line and checked by furnace engineers ([Sensors 2025](https://www.mdpi.com/1424-8220/25/13/3980)).
3. Convergent cross mapping with the embedding dimension chosen by cross-validation.
4. A joint lag vector optimised together (grey relation or PSO), because estimating one lag at a time on the full record and then freezing it is itself a source of error.
5. A coarse-to-fine search: localise the lag, refine it, then nudge it with a physical prior (burden descent time, PCI combustion time).

Report the lag, the method, the significance test, and the production-rate regime it was estimated in. Lags scale with burden descent rate. A lag fit at 10,000 t/day is the wrong lag at 8,000 t/day.

## 4. What hourly data can and cannot see

Hourly sampling can see the lags in the table above. It cannot see:

- the 10-minute PCI hydrocarbon peak, unless the historian also exports within-hour variance,
- slips and hangs (Tata's definitions are 50 mm and 100 mm radar steps; stockrods need about 2-second sampling to classify them),
- channeling precursors that China Steel detects 10–15 minutes ahead from shaft-pressure RMS,
- tuyere-nose water leaks in the minutes before top-gas hydrogen moves.

If the export includes within-hour standard deviation, minimum, maximum, and excursion counts, part of that sub-hourly behaviour comes back as an hourly feature. Ask for it. The request is in [../DATA_REQUEST.md](../DATA_REQUEST.md).

## 5. Feature rules that follow from the lags

- Build lag features per variable. A single `lag=1` on every column will miss the burden and invent skill on the blast.
- For PCI, allow two lags. The published response is bimodal.
- Size the validation embargo from the measured decorrelation time of the target (where autocorrelation falls below about 2/√n), not from a fixed 1-hour gap. Hot metal temperature needs an embargo of many hours. See [07-ml-literature.md](07-ml-literature.md).
- Do not attribute a production change to whatever moved in the same hour. Burden-side causes sit 6–8 hours upstream, and a same-hour explainer will assign them to the blast.
