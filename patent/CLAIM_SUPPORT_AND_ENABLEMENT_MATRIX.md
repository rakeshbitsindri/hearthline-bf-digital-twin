# Claim Support and Enablement Matrix

This matrix maps proposed claim limitations to the written description, figures, implementation, and tests. It helps counsel assess 35 U.S.C. 112(a)/(b), India Section 10 sufficiency, and amendment support.

| Claim limitation | Written-description support | Drawing | Working implementation | Test/evidence |
|---|---|---|---|---|
| Read-only historian interface lacking plant write paths | US Sections 3, 7.1; India Sections 5, 7.1 | FIG. 1 (106), FIG. 8 | `apps/api/bf_twin/connector.py::enforce_readonly_op`, connector profiles, `/connector/probe` | Endpoint returns HTTP 403 for write, SQL, OPC method, setpoint push |
| Mutually exclusive causal roles | US 7.2; India 7.2 | FIG. 3 (302-312) | `MANIPULATED_AND_DISTURBANCE`, parameter catalog roles, `PHYSICS_REQUIRES` | Catalog and capability tests |
| Qualified regime gate | US 7.3; India 7.3 | FIG. 1 (112) | `operating_regime`, `REGIME_ON_WIND_FRAC`, `REGIME_REDUCED_FRAC` | `test_unqualified_regime_suppresses_absolute_values` |
| Required-production-conditioned operating bands | US 7.4; India 7.4 | FIG. 4 (114) | `compute_golden_ranges` | `test_golden_ranges_scale_with_required_production_for_all_parameters` |
| Per-tag physical lag convolution | US 7.5; India 7.5 | FIG. 5 (116) | `LAG_TAU_HOURS`, `attribute_historical_shortfall` lag-active EMA | Historical shortfall tests |
| Unchanged-input shortfall diagnosis | US 7.6-7.7; India 7.6 | FIG. 2 (210-214) | `attribute_historical_shortfall`, `scan_historical_shortfalls` | `test_simulate_flags_below_and_above_golden_range_and_historical_shortfall_causes` |
| Dual Golden-Band and rolling-reference comparison | US 7.6; India 7.6 | FIGS. 2, 4, 5 | `golden_spec`, `ref_win`, `shift_vs_72h` | Historical episode output |
| Reduced-order blast-furnace physics | US 7.8; India 7.7 | FIG. 1 (118) | `compute_physics_state` | Physics and coupling tests |
| Fixed baseline sensor anchor | US 7.10; India 7.8 | FIG. 6 (124, 614) | `physics_bias`, `apply_bias` | `test_physics_is_reconciled_onto_measured_sensors` |
| Zero-change identity | US 7.10; India 7.8 | FIG. 6 (616) | Fixed anchor plus baseline-preserving final state | `test_zero_change_identity_nothing_moves` |
| Exact pressure conservation | US 7.10; India 7.8 | FIG. 6 (616) | `dP = dPu + dPl`, Ph response treatment | Pressure identity tests |
| Derivative-preserving soft saturation | US 7.9; India 7.8 | FIG. 6 (610) | `_soft_limit` | `test_soft_limit_keeps_downstream_response_alive_at_a_ceiling` |
| Fixed baseline sensor anchor and pressure identity inside the independent method claim | US 7.10 and amended claim 1; India 7.8 and amended claim 1 | FIG. 6 | `physics_bias`, `dP = dPu + dPl` | `test_physics_is_reconciled_onto_measured_sensors` |
| Separate forecast and decision residuals | US 7.11; dependent claim 10; India dependent treatment | FIG. 1 (120, 122) | Forecast model plus lag-aligned Jacobian. Full backdoor, g-computation, and double machine learning are not deployed. | Dependent only. Do not recite the three estimators as implemented. |
| Joint Mahalanobis envelope | US 7.12; India 7.9 | FIG. 7 (128) | `_envelope_distribution`, `evaluate_density_envelope` | `test_trl7_harness_rbac_sha256_audit_sse_and_mahalanobis_envelope` |
| Local step trust region | US 7.12; India 7.9 | FIG. 7 (128) | `trust_step_distance`, `trust_region_ok` | Same envelope test |
| Five physical productivity ceilings | US 7.13; India 7.9 | FIG. 7 (130) | `compute_physics_state` ceilings and binding ceiling | API responses and optimization tests |
| MoC trial dossier when candidate unsupported | US 7.15; India 7.10 | FIG. 7 (134) | `moc_dossier`, routine setpoint gate | Same envelope test |
| Evidence/capability classifier and absolute-value withholding | US 7.14; India 7.10 | FIG. 1, operator interface | `classify_physics`, `kpi_status.show_absolute` | `test_physics_is_reconciled_onto_measured_sensors`, regime test |
| Role-based hash-chained audit | US 7.15; India 7.11 | FIG. 8 (136) | `apps/api/bf_twin/db.py`, `verify_audit_chain` | TRL harness test |
| Separate confirmed execution | US 7.15; India 7.11 | FIG. 8 (138, 810) | `record_confirmed_execution` separate columns | TRL harness test |
| Monotonic SSE sequence stream | US dependent claim 19 | FIG. 1 | `sse_shadow_stream`, `/stream/live` | SSE test |

## Disclosure gaps to resolve before filing

1. **Decision residual plurality:** The architecture specifies forecast and decision residual families. The present coupled simulator uses a lag-aligned regularized Jacobian and physics deltas; a complete backdoor/g-computation/DML decision-residual implementation is a future phase. Claims should not assert that all three causal estimators are currently deployed.
2. **Measured production example:** EVRAZ public data lacks measured hot-metal tonnage. Production examples on that data are stoichiometric/permeability estimates and must be labelled accordingly. Add a customer or synthetic full-sensor example without representing synthetic data as metallurgical validation.
3. **Target-band sensitivities:** Some `loss_per_unit` and scale sensitivities are engineering configuration values pending plant validation. Claim the method, not universal numerical coefficients.
4. **Comparative experiment:** Add a table showing hard clipping versus soft saturation, free-running versus anchored error, and zero-change drift before/after.
5. **Inventorship evidence:** Preserve commits, design notes, messages, and contributor records mapping conception of each feature.
6. **Figures:** Export `PATENT_DRAWINGS.html` into Patent Office-compliant black-and-white PDF and verify margin/reference-sign requirements.

