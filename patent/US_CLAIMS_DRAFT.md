# Draft United States Claims

Attorney review required. The set contains 20 total claims and two independent claims to fit a common initial US fee structure.

## What is claimed is:

1. **A method for identifying an unmeasured physical cause of a hot-metal production shortfall in an iron blast furnace while operator-set inputs remain inside a production-conditioned band, the method comprising:**

   receiving, through a historian interface restricted to read operations, time-series records from a plurality of sensors associated with the blast furnace;

   assigning each of a plurality of furnace tags represented in the time-series records to one of a plurality of mutually exclusive causal roles comprising a manipulated input, a disturbance, a furnace state response, an outcome, or a derived latent state;

   receiving a required hot-metal production rate;

   for each of at least a subset of the furnace tags, generating a production-conditioned operating band by:

   (a) selecting, from historical qualified on-wind periods, a cohort having a production measure within a production tolerance of the required hot-metal production rate and having a pressure-drop measure below a permeability criterion,

   (b) determining lower, center, and upper empirical values from the cohort, and

   (c) shifting at least one of the empirical values according to a physical production-intensity sensitivity and a difference between the required hot-metal production rate and a production measure of the cohort;

   at a query time, generating a lag-active value for each of the subset of furnace tags by applying a respective temporal kernel parameterized by a physical transport delay of the corresponding furnace tag;

   detecting an unchanged-input production-shortfall interval in which a production value is below at least one of the required hot-metal production rate or a preceding rolling production reference while a selected plurality of the manipulated inputs remain within corresponding production-conditioned operating bands;

   during the unchanged-input production-shortfall interval, identifying an unmeasured furnace condition as the cause of the production shortfall by ranking a measured disturbance or furnace state response whose lag-active value deviates from both (i) its production-conditioned operating band and (ii) a preceding rolling tag reference, the unmeasured furnace condition comprising at least one of an alkali or zinc accumulation, a burden-permeability loss, a cohesive-zone shift, a circumferential gas maldistribution, or a hearth-drainage restriction;

   generating a counterfactual recovery trajectory for at least one candidate manipulated-input vector with a reduced-order blast-furnace material-and-energy calculation reconciled to the sensors, wherein generating the counterfactual recovery trajectory comprises:

   computing an additive anchor bias at a baseline state as a difference between a measured furnace response and a free-running output of the reduced-order blast-furnace physics model,

   holding the additive anchor bias fixed while evaluating the candidate manipulated-input vector, and

   enforcing a pressure conservation identity in which a simulated total pressure drop equals a sum of an upper-furnace pressure drop and a lower-furnace pressure drop;

   determining whether the candidate manipulated-input vector is inside a joint-density operating envelope and a trust region and satisfies a plurality of physical blast-furnace productivity ceilings; and

   responsive to determining that the candidate manipulated-input vector is inside the joint-density operating envelope and the trust region and satisfies the plurality of physical blast-furnace productivity ceilings, outputting the candidate manipulated-input vector as the safety-gated operator advisory, and otherwise withholding the candidate manipulated-input vector as a routine advisory and generating an engineering-trial dossier.

2. The method of claim 1, wherein the historian interface permits one or more of an HTTP GET operation, an OPC-UA Read service, an OPC-UA HistoryRead service, or reading an immutable file, and rejects historian writes, OPC method calls, SQL mutation operations, and actuator setpoint writes.

3. The method of claim 1, wherein the physical transport delay is selected from a first gas-phase delay for blast flow or oxygen, a second injectant delay for pulverized-coal injection, a third burden-descent delay for charged coke or ore, and a fourth accumulation delay for alkali or zinc.

4. The method of claim 1, wherein the temporal kernel is an exponential moving-average kernel over an interval extending from the query time minus at least twice the physical transport delay to the query time.

5. The method of claim 1, wherein the preceding rolling tag reference excludes a recent interval immediately preceding the query time to prevent a developing event from contaminating the reference.

6. The method of claim 1, wherein the reduced-order blast-furnace physics model includes at least three selected from raceway adiabatic flame temperature, tuyere oxygen/carbon stoichiometry, bosh-gas volume, Rist operating-line quantity, upper and lower packed-bed pressure drop, top-gas utilization, cohesive-zone geometry, volatile condensation load, hot-metal temperature, silicon response, or a production ceiling.

7. The method of claim 1, further comprising confirming a zero-change identity in which, when the candidate manipulated-input vector equals a current manipulated-input vector, each anchored simulated response equals the corresponding measured baseline response within a numerical tolerance.

8. The method of claim 7, wherein the learned residual model used for the counterfactual recovery trajectory is restricted to features that are not descendants of the production outcome, and wherein a manipulated input classified as not identifiable is excluded from the safety-gated operator advisory.

9. The method of claim 1, wherein the reduced-order blast-furnace physics model applies a continuously differentiable monotonic saturation operator outside a nominal physical interval so that a response derivative remains nonzero outside the nominal physical interval.

10. The method of claim 1, wherein a forecast residual used to predict a future outcome is permitted to use information known at forecast time, and a separate decision residual used to score the candidate manipulated-input vector is restricted to causal-parent features of the outcome.

11. The method of claim 1, wherein the joint-density operating envelope comprises a regularized Mahalanobis ellipsoid fitted to historical qualified on-wind manipulated-input vectors and the trust region comprises a Mahalanobis step distance from a current manipulated-input vector.

12. The method of claim 1, wherein the plurality of physical blast-furnace productivity ceilings comprises at least three of a tuyere stoichiometry ceiling, a packed-bed permeability ceiling, a gas flooding or fluidization ceiling, a top-gas thermal or dewpoint ceiling, or a hearth drainage ceiling, and the method further comprises reporting a lowest ceiling as a binding ceiling.

13. The method of claim 1, further comprising storing an operator acceptance or rejection of the safety-gated operator advisory in a hash-chained append-only record and storing later confirmation that a plant action occurred in a separate post-hoc execution field that does not alter the hash of the operator acceptance or rejection.

14. **A system for identifying an unmeasured physical cause of a hot-metal production shortfall in an iron blast furnace, the system comprising:**

   a historian interface configured to receive time-series records from furnace sensors while lacking a write path to a plant historian, programmable logic controller, distributed control system, or furnace actuator;

   one or more processors; and

   memory storing instructions that, when executed by the one or more processors, cause the system to:

   classify furnace tags into mutually exclusive causal roles comprising manipulated inputs, disturbances, furnace state responses, outcomes, and derived latent states;

   form, for a required hot-metal production rate, respective target-conditioned operating bands from a permeability-qualified historical production cohort;

   transform values of the furnace tags into lag-active values using tag-specific temporal kernels representing physical transport delays within the blast furnace;

   detect a production shortfall during an interval in which selected manipulated inputs remain within the respective target-conditioned operating bands;

   attribute the production shortfall to an unmeasured furnace condition inferred from one or more lag-active disturbances or furnace state responses that have left their target-conditioned operating bands;

   anchor a reduced-order blast-furnace material-and-energy calculation to current measured sensor responses and use that anchored calculation to test a candidate recovery;

   evaluate the candidate recovery advisory against a joint historical operating-density envelope, a local trust region, and multiple physical blast-furnace productivity ceilings; and

   selectively output the candidate recovery advisory or an engineering-trial dossier according to the evaluation.

15. The system of claim 14, wherein the system is configured to output, for each attributed cause, a furnace tag, a tag-specific lag, a lag-active value, a target-conditioned operating band, an estimated production-loss contribution, and a physical mechanism.

16. The system of claim 14, wherein the system includes a capability classifier configured to classify a result as measured-anchored, physics-estimated, assumption-dependent, response-only, not-qualified, not-identifiable, or not-testable.

17. The system of claim 16, wherein the capability classifier withholds an absolute value of a derived latent state while permitting a differential counterfactual response when required measured inputs are absent.

18. The system of claim 14, wherein the system is configured to suppress the candidate recovery advisory during at least one of off-wind operation, banking, blow-in, shutdown, maintenance, stale-source operation, severe instability, or an unqualified regime.

19. The system of claim 14, wherein the system is configured to publish server-sent events containing monotonic sequence numbers, a model version, a regime status, an operating-envelope status, and a target-band compliance value.

20. The system of claim 14, further comprising a role-based audit service configured to permit acceptance or rejection by an operator role, calibration sign-off by a metallurgist role, and read-only inspection by an auditor role, while maintaining a cryptographic hash chain across audit events.

