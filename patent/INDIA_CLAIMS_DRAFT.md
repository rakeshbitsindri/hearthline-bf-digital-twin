# Draft Claims for Indian Complete Specification

These claims are intentionally framed as an industrial furnace-monitoring process and apparatus producing a technical effect on physical-process diagnosis, rather than as a computer program per se or algorithm. Registered Indian patent-agent review is required.

## I/We claim:

1. **A method for sensor-based diagnosis of a physical production shortfall in an iron blast furnace by a read-only industrial furnace-monitoring apparatus coupled to a plurality of blast-furnace sensors, the method comprising:**

   receiving, through an industrial historian interface restricted to read services, time-series physical measurements comprising manipulated furnace inputs, material disturbances, furnace state responses, and hot-metal production or quality outcomes;

   assigning each physical measurement to one mutually exclusive causal role comprising manipulated input, disturbance, furnace state response, outcome, or derived latent state;

   for a required hot-metal production rate, selecting a historical cohort of qualified on-wind furnace intervals having production within a tolerance of the required hot-metal production rate and pressure drop below a permeability criterion, and generating from the historical cohort a lower operating value, center operating value, and upper operating value for each of a plurality of furnace tags;

   shifting at least one of the lower, center, or upper operating values according to a physical furnace sensitivity and a difference between the required hot-metal production rate and production represented by the historical cohort, thereby producing a production-conditioned operating band;

   converting each of the plurality of furnace tags at a query time into a lag-active physical value by applying a respective temporal kernel representing a gas-flow delay, injectant delay, descending-burden delay, thermal delay, or accumulated-inventory delay within the blast furnace;

   detecting an unchanged-input shortfall in which a measured or reconciled production value is below the required hot-metal production rate or below a preceding rolling production reference while a selected plurality of manipulated inputs remain within their corresponding production-conditioned operating bands;

   in response to the unchanged-input shortfall, identifying at least one material disturbance or furnace state response as a physical cause according to a deviation of the lag-active physical value from both its production-conditioned operating band and a preceding rolling reference of the corresponding furnace tag;

   generating a counterfactual recovery trajectory with a reduced-order blast-furnace physical model reconciled to current physical sensor measurements and a learned residual restricted to selected causal-parent measurements;

   evaluating the counterfactual recovery trajectory against a joint multi-parameter historical operating-density envelope, a step trust region, and a plurality of physical blast-furnace productivity ceilings; and

   displaying, through an operator advisory interface, either (i) a recovery advisory when the counterfactual recovery trajectory remains within said envelope, trust region, and productivity ceilings, or (ii) an engineering-trial dossier while withholding the recovery advisory when at least one of said envelope, trust region, or productivity ceilings is violated.

2. The method as claimed in claim 1, wherein the industrial historian interface permits only an HTTP read operation, an OPC-UA Read service, an OPC-UA HistoryRead service, or reading an immutable historian-export file, and rejects historian write, OPC method-call, SQL mutation, programmable-logic-controller write, distributed-control-system setpoint, and furnace-actuator operations.

3. The method as claimed in claim 1, wherein the reduced-order blast-furnace physical model is anchored at a baseline by calculating an additive bias between a measured sensor response and a free-running physical-model output, holding said additive bias fixed during the counterfactual recovery trajectory, and enforcing a physical identity in which total furnace pressure drop equals upper-furnace pressure drop plus lower-furnace pressure drop.

4. The method as claimed in claim 3, wherein the reduced-order blast-furnace physical model applies a monotonic continuously differentiable saturation function outside a nominal physical interval, thereby retaining a non-zero response sensitivity at a furnace operating limit.

5. The method as claimed in claim 1, wherein the joint multi-parameter historical operating-density envelope is a regularized Mahalanobis ellipsoid fitted to qualified on-wind manipulated-input vectors and the step trust region is a Mahalanobis distance from a current manipulated-input vector.

6. The method as claimed in claim 1, wherein the plurality of physical blast-furnace productivity ceilings includes at least three selected from tuyere oxygen-carbon stoichiometry, packed-bed pressure-drop permeability, bosh-gas flooding or fluidization, top-gas thermal or acid-dewpoint condition, and hearth coke-bed drainage, and wherein a lowest ceiling is displayed as a binding ceiling.

7. The method as claimed in claim 1, further comprising classifying each generated result as measured-anchored, physics-estimated, assumption-dependent, response-only, not-qualified, not-identifiable, or not-testable, and withholding an absolute latent-state value while continuing to display a differential response when a required sensor is unavailable.

8. The method as claimed in claim 1, further comprising storing an operator acceptance or rejection in an append-only cryptographic hash chain stamped with a model version and storing a later indication of plant execution in a separate post-hoc field without altering the operator acceptance or rejection.

9. **A blast-furnace advisory apparatus comprising:**

   a plurality of industrial data inputs receiving physical blast-furnace sensor measurements;

   a read-only historian interface configured to receive said measurements while lacking a write service to a historian, programmable logic controller, distributed control system, or furnace actuator;

   one or more processors; and

   a memory storing executable instructions configured to cause the apparatus to perform the method of any one of claims 1 to 8.

10. The blast-furnace advisory apparatus as claimed in claim 9, further comprising a regime gate configured to suppress a recovery advisory during off-wind operation, banking, blow-in, shutdown, maintenance, stale-source operation, severe instability, or an unqualified regime.

