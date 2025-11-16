# FRE Simulator V2.0

**FRE Simulator V2.0** is an experimental computational module designed to simulate
the structural dynamics of the **Flexionization Risk Engine (FRE)**.

The simulator is used to explore stability, FXI behaviour, reactions to shocks,  
and corrective operators within the FRE-2.0 framework.

> Note: This simulator is a research-grade computational tool.
> It does not replace the formal mathematical specification of FRE-2.0.

---

## 1. Purpose

The simulator provides a numerical environment for exploring the structural
behaviour of the Flexionization Risk Engine. It implements the core components
of the FRE-2.0 model and allows controlled experimentation with different
operators, shocks, and initial configurations.

The primary objectives are:

- simulate step-by-step system evolution;
- observe Δ(t) and FXI(t) dynamics;
- evaluate corrective operators \(E\);
- run stress scenarios and shock sequences;
- detect stability zones;
- compute contractivity (κ);
- identify capacity breaches and structural fragility.

The simulator enables direct comparison of operators, scenarios, 
and initial structural states under a unified FRE framework.

---

## 2. Theoretical Foundation

FRE Simulator V2.0 is based on the mathematical structure of the
**Flexionization Risk Engine (FRE)**.  
The simulator does not define the theory — it numerically evaluates it.

The underlying framework includes:

- the structural state of the system;
- the deviation function Δ(t);
- the Flexionization Equilibrium Index (FXI);
- the corrective operator \(E\);
- continuity and boundedness rules;
- contractivity and stability conditions;
- structural evolution over discrete time steps.

The complete formal specification is provided in the LaTeX documentation
of FRE-2.0 located in the parent directory of this module.

---

## 3. Project Structure

The FRE Simulator is organized as a standalone module inside the FRE-V2.0 repository. Its directory layout is structured to separate theory, computation, scenarios, and visualization.

FRE-simulator/
├── README.md                   # documentation for the simulator
├── requirements.txt            # Python dependencies
├── notebooks/
│   └── FRE-Simulator-V2.0-demo.ipynb   # demo scenarios
└── src/
    └── fre_simulator/
        ├── __init__.py
        ├── state.py            # structural state, Δ, FXI, validation
        ├── operators.py        # corrective operators E, kappa tools
        ├── scenarios.py        # stress scenarios
        ├── engine.py           # simulation loop and evolution logic
        └── visualization.py    # plotting and stability zone rendering

Each module serves a specific purpose:

- **state.py** — defines the structural state representation and enforces admissible conditions for Δ(t), FXI(t), and system components.
- **operators.py** — implements corrective operators \(E\), FXI update rules, and tools for computing contractivity κ.
- **scenarios.py** — provides deterministic and stochastic shocks, regime changes, and stress-test templates.
- **engine.py** — executes the step-by-step evolution loop, applies scenario events, updates Δ and FXI, invokes the operator, and logs all outputs.
- **visualization.py** — produces time-series charts, stability zone plots, FXI trajectories, and export utilities (PNG/CSV/JSON).

---

## 4. Core Components

FRE Simulator V2.0 is built around five core modules that implement the structural logic of the FRE model. Each module corresponds to a specific aspect of the simulation pipeline and mirrors the formal structure of the FRE-2.0 theoretical specification.

### 4.1 state.py  
Defines the structural state of the system, including all required components such as Δ(t), FXI(t), and any auxiliary variables.  
This module enforces admissibility constraints, validates inputs, and provides helpers for constructing initial system states.

### 4.2 operators.py  
Implements the corrective operator \(E\) used in FRE.  
Provides functionality for computing FXI updates, measuring contractivity κ, evaluating stability conditions, and generating local/global κ maps.

### 4.3 scenarios.py  
Defines deterministic and stochastic scenarios, including shocks, parameter shifts, multi-step stress sequences, and regime transitions.  
This module standardizes stress-test definitions for reproducible experiments.

### 4.4 engine.py  
Implements the core step-by-step evolution loop of the FRE model.  
At each iteration it applies scenario events, updates Δ(t) and FXI(t), invokes the corrective operator \(E\), tracks stability zones, checks capacity boundaries, and logs the full trajectory.

### 4.5 visualization.py  
Provides plotting utilities for Δ(t), FXI(t), structural trajectories, and stability zones.  
Supports export of figures and time-series data in PNG, CSV, and JSON formats, enabling external analysis and reporting.

---

## 5. Installation

FRE Simulator V2.0 is implemented in Python and relies on a lightweight set of scientific dependencies. The simulator can be used in scripts or Jupyter notebooks after installing the required packages.

To install dependencies, use the command:

pip install -r requirements.txt

### Environment Notes
- Python 3.9 or newer is recommended.
- No GPU or special hardware is required.
- All modules under `src/fre_simulator/` can be imported directly once dependencies are installed.

After installation, the simulator is ready for running experiments, stress tests, and structural evolution scenarios within the FRE framework.

---

## 6. Development Status

FRE Simulator V2.0 is currently under active development.  
The structural layout of the module is complete, and the core interfaces are defined, but several components are still being implemented and refined.

### Current Progress
- ✔ Project structure finalized  
- ✔ Core modules created  
- ⏳ Implementation of corrective operators \(E\)  
- ⏳ Full evolution engine logic  
- ⏳ Stress-scenario library  
- ⏳ Visualization utilities  
- ⏳ Unit tests and validation suite  

The simulator is considered a research-grade tool. Its purpose is to support the exploration, testing, and validation of FRE-2.0 concepts as the theoretical model evolves.

---

## 7. License

The FRE Simulator V2.0 follows the same licensing terms as the main
Flexionization Risk Engine project. All rights, usage permissions,
and distribution rules are inherited from the parent repository.

This module is intended for research, analysis, and development
within the Flexionization framework and should be used in accordance
with the licensing policy defined at the root of the project.

---

## 8. Quickstart Example

This section provides a minimal example of how to run a basic FRE simulation.  
The example shows how to initialize the structural state, select the corrective
operator, choose a scenario, and run the simulation loop.

### 8.1 Initial State
You begin by constructing the initial structural state \( S_0 \), which contains
all system components including Δ, FXI, and operational variables.

### 8.2 Corrective Operator
Choose the operator \( E \) that defines how FXI evolves at each time step.
The simulator provides a default operator for testing.

### 8.3 Scenario
Select a scenario to define external shocks or system events.  
An empty scenario applies no shocks.

### 8.4 Running the Simulation
Call the main `run_simulation` function to execute a full evolution cycle over
a specified horizon.

### 8.5 Example Code

from fre_simulator.engine import run_simulation  
from fre_simulator.state import initial_state  
from fre_simulator.operators import DefaultOperator  
from fre_simulator.scenarios import EmptyScenario  

S0 = initial_state(  
    delta=0.0,  
    fxi=1.0,  
    qp=1.0,  
    qf=1.0,  
    q=1.0,  
    w=1.0,  
    u=1.0  
)

operator = DefaultOperator()  
scenario = EmptyScenario()

result = run_simulation(  
    initial_state=S0,  
    operator=operator,  
    scenario=scenario,  
    horizon=100  
)

print(result.fxi_series)  
print(result.delta_series)

### 8.6 Output
After running, the simulator returns structured time series containing:
- FXI trajectory,
- Δ trajectory,
- stability diagnostics,
- scenario events,
- operator behaviour metrics.

This provides the minimal setup needed to start experimenting with FRE dynamics.

---

## 9. API Reference

This section provides a concise reference for the core public functions and classes
exposed by the FRE Simulator module. It covers the essential interfaces required to
define system states, operators, scenarios, and to execute full simulation cycles.

### 9.1 State API (state.py)

**initial_state(...)**  
Creates and validates the initial structural state \( S_0 \).  
Parameters include Δ, FXI, and all operational variables.

**State object fields:**
- delta — current deviation Δ(t)
- fxi — current FXI(t)
- qp, qf — primary and feedback quantities
- q — structural parameter
- w, u — auxiliary operational variables

The state object ensures all values are admissible.

### 9.2 Operator API (operators.py)

**DefaultOperator()**  
Built-in corrective operator implementing the baseline FXI update rule.

**operator.apply(fxi_value)**  
Computes the next FXI value under operator \( E \).

**operator.kappa(prev_fxi, next_fxi)**  
Returns the contractivity coefficient κ based on two consecutive FXI values.

### 9.3 Scenario API (scenarios.py)

**EmptyScenario()**  
A scenario that applies no shocks and keeps all variables unchanged.

**scenario.apply(state, t)**  
Applies a shock or parameter update to the state at time step t.

Custom scenarios define time-varying changes to qp, qf, q, w, u, or Δ.

### 9.4 Engine API (engine.py)

**run_simulation(initial_state, operator, scenario, horizon)**  
Executes the FRE evolution loop over the specified number of steps.

Returns a result object with:
- fxi_series — list of FXI values over time
- delta_series — list of Δ values over time
- state_series — full history of structural states
- kappa_series — contractivity diagnostics
- stability_zones — classification of each step (stable, stressed, critical)

### 9.5 Visualization API (visualization.py)

**plot_fxi(result)**  
Renders FXI trajectory over time.

**plot_delta(result)**  
Shows Δ(t) evolution.

**plot_stability_zones(result)**  
Highlights stable, stressed, and critical zones.

These tools allow direct visual analysis of system behaviour and operator effects.

---

## 10. Simulation Workflow

This section describes the full execution flow of an FRE simulation.  
The workflow outlines how the initial state, operator, and scenario interact
inside the evolution loop to generate structural trajectories.

### 10.1 Step 1 — Initialize the Structural State
The simulation begins by creating the initial state \( S_0 \).  
All components (Δ, FXI, qp, qf, q, w, u) must satisfy admissibility rules
defined in the FRE specification.

### 10.2 Step 2 — Select Corrective Operator E
The operator \( E \) defines how FXI evolves.  
Each operator must implement:
- an FXI update function,
- contractivity diagnostics (κ),
- optional operator-specific parameters.

Different operators may lead to different stability regimes.

### 10.3 Step 3 — Select Scenario
A scenario defines external events such as shocks, parameter shifts,
or structural disturbances applied at specific time steps.
Scenarios may be:
- deterministic,
- stochastic,
- multi-step stress sequences,
- or completely empty.

### 10.4 Step 4 — Run the Evolution Loop
The engine iterates from t = 0 to t = horizon − 1.  
At each step it:
1. Applies the scenario event for time t.  
2. Updates Δ(t) based on system structure.  
3. Computes FXI(t+1) via operator \( E \).  
4. Evaluates stability zone for the current step.  
5. Computes contractivity κ.  
6. Records the state and diagnostics.

### 10.5 Step 5 — Produce Simulation Results
After the loop completes, the engine returns a structured result object
containing:
- FXI trajectory,
- Δ trajectory,
- full state history,
- stability classification,
- κ values,
- scenario events log.

These outputs form the basis for structural analysis, stress testing,
and the validation of FRE operators.

---

## 11. Advanced Scenarios

Advanced scenarios extend the basic shock model by introducing multi-stage,
stochastic, and structural transformation events. These scenarios allow deeper
analysis of system fragility, structural resilience, and the long-term effects
of corrective operators.

### 11.1 Multi-Step Shock Sequences
A sequence of shocks applied across several time steps.  
Examples include:
- progressive liquidity withdrawal,
- repeated parameter oscillations,
- staged regime tightening or relaxation.

Such sequences evaluate how the system reacts to persistent pressure.

### 11.2 Stochastic Scenarios
Random shocks generated from predefined distributions (e.g., normal,
uniform, or heavy-tailed).  
Useful for:
- Monte Carlo stress testing,
- robustness evaluation,
- operator sensitivity analysis.

Each run may produce different trajectories based on random inputs.

### 11.3 Regime Switching Scenarios
Scenarios that introduce discrete regime changes such as:
- sudden parameter changes,
- structural reconfiguration of qp, qf, or q,
- transitions between stable and stressed states.

This models systems that operate under multiple operational regimes.

### 11.4 Composite Stress Tests
Combines deterministic and stochastic components, for example:
- deterministic shock at t = 5,
- followed by a stochastic disturbance until t = 20,
- and a final structural reset.

This is used to test recovery ability after complex compound stress events.

### 11.5 Scenario Diagnostics
Every advanced scenario provides:
- a log of all applied shocks,
- indicators of structural deformation,
- recovery or divergence trends,
- stress persistence patterns.

Advanced scenarios enable the evaluation of FRE operator behaviour under
nonlinear, persistent, or unpredictable conditions, providing deeper insight
into system-level risk dynamics.

---

## 12. Operator Design Guide

This section provides guidelines for designing new corrective operators \(E\)
within the FRE-2.0 framework. Operators are central to the behaviour of FXI
and determine the system’s stability, contractivity, and recovery profile.

### 12.1 Core Requirements for Operators
Every operator \(E\) must satisfy the structural principles of FRE:
- **Continuity** — small changes in FXI should produce small changes in \(E(FXI)\).
- **Boundedness** — the operator must not allow unbounded divergence.
- **Stability orientation** — \(E(FXI)\) should guide FXI toward equilibrium.
- **Contractivity** — in the stable region, κ must satisfy \(κ < 1\).

Operators that violate these principles may produce unstable trajectories.

### 12.2 Designing the FXI Update Rule
An operator defines how FXI evolves:
\[
FXI_{t+1} = E(FXI_t)
\]
Design considerations:
- monotonic vs. non-monotonic response,
- strength of correction near equilibrium,
- behaviour far from equilibrium,
- saturation effects or upper/lower bounds.

### 12.3 Tuning Contractivity (κ)
Contractivity is a key metric for operator performance:
\[
κ = \frac{|FXI_{t+1} - 1|}{|FXI_t - 1|}
\]
Guidelines:
- κ close to 0 → fast convergence,
- 0 < κ < 1 → stable correction,
- κ ≥ 1 → loss of stability.

Operators must be tuned to ensure κ remains below 1 across expected conditions.

### 12.4 Handling Extreme Conditions
Operators should account for:
- large deviations Δ,
- extreme FXI movements,
- shocks applied by scenarios,
- boundary conditions on qp, qf, q, w, u.

This ensures robustness under stress-testing.

### 12.5 Testing a New Operator
When adding a new operator:
1. Define the FXI update rule.  
2. Validate continuity and boundedness.  
3. Test contractivity across a grid of FXI values.  
4. Run baseline scenarios (empty, single-shock, progressive-shock).  
5. Compare the trajectories to reference operators.  

### 12.6 Implementation Notes
Operators are implemented as simple Python classes with:
- an `apply()` method for FXI evolution,
- a `kappa()` function for contractivity,
- optional internal parameters.

The design should remain modular so new operators integrate cleanly with the
rest of the FRE Simulator ecosystem.

---

## 13. Stability Zones

Stability zones classify the system’s behaviour at each time step based on the
current value of the Flexionization Equilibrium Index (FXI). These zones provide
a clear interpretation of how far the system is from equilibrium and how the
operator \(E\) is performing in stabilizing the structure.

### 13.1 Zone Definitions

The simulator classifies each time step into one of three zones:

- **Stable Zone**  
  FXI is close to equilibrium.  
  The system demonstrates controlled, contractive behaviour.

- **Stressed Zone**  
  FXI deviates moderately from 1.  
  The system remains functional but shows signs of structural tension.

- **Critical Zone**  
  FXI deviates strongly from equilibrium.  
  The system exhibits instability, elevated κ, or operator saturation.

### 13.2 Zone Determination Criteria

Zones are assigned using absolute deviation thresholds:

- Stable:  \(|FXI - 1| \le ε_1\)  
- Stressed: \(ε_1 < |FXI - 1| \le ε_2\)  
- Critical: \(|FXI - 1| > ε_2\)

The values of \(ε_1\) and \(ε_2\) may be tuned depending on the model.

### 13.3 Interpretation

- **Stable Zone** indicates proper functioning of the corrective operator
  and consistent convergence toward equilibrium.

- **Stressed Zone** signals increased structural pressure but does not imply
  failure. Operator behaviour should be evaluated.

- **Critical Zone** represents a breakdown of contractivity or extreme deviation
  conditions. FXI may require intervention or a stronger operator.

### 13.4 Simulator Output

The result object includes a `stability_zones` field, containing a zone label
for every time step.  
This allows:

- visualization of stability segments,  
- comparison across operators,  
- stress-test diagnostics,  
- detection of transitions between zones.

Stability zones form one of the core diagnostic layers of FRE Simulator V2.0.

---

## 14. Capacity Breach Logic

Capacity breach detection is a core diagnostic mechanism of the FRE Simulator.
It identifies when the system exceeds predefined structural limits, indicating
a breakdown in operational capacity or a failure of corrective dynamics.

### 14.1 Purpose of Breach Detection

Capacity limits represent the boundaries within which the structural model is
intended to operate. A breach signals that one or more components have moved
outside the admissible region due to shocks, unstable operator behaviour, or
extreme deviations.

Breach detection is therefore essential for:
- evaluating risk exposure,
- identifying operator failure modes,
- validating stability under stress,
- detecting non-recoverable structural states.

### 14.2 Types of Capacity Constraints

The simulator monitors multiple structural constraints, including:

- **Deviation Bound**  
  Maximum allowed magnitude of Δ(t).

- **FXI Boundaries**  
  Extreme values of FXI beyond which the model loses structural meaning.

- **Operational Limits**  
  Constraints on qp, qf, q, w, or u depending on model configuration.

Each constraint is defined as a threshold that determines when the system
enters an inadmissible region.

### 14.3 Breach Conditions

A capacity breach occurs if any monitored component violates its threshold:

- \(|Δ| > Δ_{\max}\)  
- \(FXI < FXI_{\min}\) or \(FXI > FXI_{\max}\)  
- qp, qf, q, w, or u exceed allowed operational limits

The simulator checks these conditions at every time step.

### 14.4 Breach Event Recording

When a breach is detected, the simulator records:

- **breach flag** — indicating that a violation occurred,  
- **breach time** — the first time step of violation,  
- **breach state** — the full system state at the moment of breach,  
- **breach type** — the specific constraint that failed.

This enables detailed forensic analysis of stability failure.

### 14.5 Interpretation

A capacity breach typically indicates one of the following:

- the operator \(E\) is not sufficiently stabilizing,  
- the scenario applies excessive stress,  
- the system configuration is structurally unsound,  
- the model has entered a non-physical or undefined region.

Breaches provide a clear threshold for evaluating system robustness.

### 14.6 Simulator Output

The `result` object contains fields such as:

- `breach_occurred` — true/false  
- `breach_step` — time index of violation  
- `breach_state` — structural snapshot  
- `breach_type` — category of failed constraint

This information is essential for diagnosing extreme or catastrophic model behaviour.

---

## 15. Result Object Specification

The result object returned by the FRE simulation engine provides a complete,
structured record of all system variables, diagnostics, and events generated
during the evolution process. This object is the primary interface for analysis,
visualization, and downstream processing.

### 15.1 Core Time Series

The result contains the following step-by-step trajectories:

- **fxi_series**  
  The full sequence of FXI(t) values.

- **delta_series**  
  The deviation Δ(t) across all time steps.

- **state_series**  
  Complete structural states, including qp, qf, q, w, and u.

These series allow reconstruction of the entire system evolution.

### 15.2 Stability Diagnostics

The engine assigns a stability zone to each time step:

- **stability_zones**  
  A list of zone labels: “stable”, “stressed”, or “critical”.

These labels are derived from FXI deviation thresholds.

### 15.3 Contractivity Metrics

The simulator computes contractivity values:

- **kappa_series**  
  A sequence of κ values evaluating operator behaviour at each step.

Values κ < 1 indicate contractive behaviour; κ ≥ 1 indicates loss of stability.

### 15.4 Scenario Event Log

The result may also include:

- **scenario_events**  
  A chronological record of shocks or parameter updates applied at each time step.

This helps analyze how scenario inputs affect structural dynamics.

### 15.5 Capacity Breach Information

If the system violates a structural constraint, the result records:

- **breach_occurred** — boolean flag  
- **breach_step** — time index of the first violation  
- **breach_state** — full snapshot of the system at the breach moment  
- **breach_type** — specific constraint that was exceeded

This allows precise identification of structural breakdowns.

### 15.6 Result Object Usage

The result object is designed for:

- plotting and visualization,
- stability and contractivity analysis,
- comparing operators,
- scenario effectiveness evaluation,
- exporting trajectories for external tools.

It serves as the comprehensive output package of FRE Simulator V2.0.

---

## 16. Parameters & Configuration

The FRE Simulator provides a flexible configuration system that allows users to
define structural parameters, simulation settings, operator behaviour, and
scenario properties. This section summarizes all key parameters and how they
influence the evolution process.

### 16.1 Structural Parameters

These parameters define the system’s internal state:

- **Δ (delta)** — deviation measure that captures structural imbalance.
- **FXI** — Flexionization Equilibrium Index.
- **qp** — primary operational quantity.
- **qf** — feedback operational quantity.
- **q** — structural parameter regulating internal balance.
- **w, u** — auxiliary operational variables that may encode liquidity, weights,
  or internal control coefficients depending on the model.

All structural parameters must remain within admissible ranges defined in the
FRE specification.

### 16.2 Operator Parameters

Corrective operators \(E\) may expose their own configuration:

- **correction_strength** — intensity of FXI adjustment.
- **equilibrium_tolerance** — how closely FXI is driven toward 1.
- **saturation_thresholds** — boundaries beyond which correction weakens.
- **nonlinearity coefficients** — for curved or adaptive operator profiles.

These parameters allow operators to be tuned for different stability regimes.

### 16.3 Scenario Parameters

Scenarios may define:

- **shock magnitude** — intensity of an applied change.
- **shock timing** — exact time steps when shocks occur.
- **shock frequency** — periodic, random, or continuous disturbances.
- **parameter shifts** — modifications to qp, qf, q, w, or u.
- **noise distribution** — for stochastic scenarios (normal, uniform, etc.).

Scenarios control external stress applied to the system.

### 16.4 Simulation Parameters

Core settings for the evolution loop:

- **horizon** — number of simulation steps.
- **logging level** — controls which diagnostics are stored.
- **zone thresholds** — values \(ε_1\) and \(ε_2\) for stability zone detection.
- **capacity limits** — thresholds for Δ, FXI, and operational variables.
- **seed** — random seed for reproducibility in stochastic scenarios.

### 16.5 Configuration Management

The simulator supports two ways of defining configuration:

- **Direct function parameters**  
  Passed explicitly into `run_simulation()` or the scenario/operator constructors.

- **Configuration dictionaries**  
  A structured Python dictionary that holds multiple settings in one place.

Example structure:

config = {  
  "horizon": 200,  
  "zone_thresholds": { "eps1": 0.02, "eps2": 0.10 },  
  "capacity_limits": { "delta": 5.0, "fxi_min": 0.5, "fxi_max": 2.0 }  
}

Configuration management allows flexible control over model behaviour and
ensures repeatability across different simulation experiments.

---

## 17. Mathematical Notes (Non-Formal)

This section provides high-level mathematical intuition behind the FRE
simulation model. It does not replace the formal specification; instead, it
helps users understand how Δ, FXI, and the corrective operator \(E\) interact
within the structural dynamics of FRE-2.0.

### 17.1 Role of Δ (Delta)
Δ represents structural deviation — a measure of how far the system has drifted
from its internal equilibrium configuration.  
Key intuition:

- Small Δ means the system is in structural alignment.
- Large Δ indicates persistent imbalance or stress.
- Δ responds to both internal dynamics and external scenario shocks.

The simulator tracks Δ as one of the core indicators of system health.

### 17.2 FXI as the Equilibrium Indicator
FXI is the central scalar indicator of equilibrium.  
Interpretation:

- FXI ≈ 1 → the system is balanced.
- FXI > 1 → structural over-extension.
- FXI < 1 → structural contraction or deficit.

FXI is easier to interpret than the full internal state and is used to classify
stability zones.

### 17.3 Corrective Operator \(E\)
The operator \(E\) defines how the system corrects itself:

FXI(t+1) = E(FXI(t))

Intuition:

- \(E\) pulls FXI toward 1.
- The curvature of \(E\) determines the aggressiveness of correction.
- Saturation or flattening of \(E\) far from equilibrium may produce slow or
  unstable dynamics.
- Sharp corrections near equilibrium may increase stability or cause overshoot,
  depending on design.

Operators essentially encode the system’s “risk control policy”.

### 17.4 Contractivity κ
κ measures how strongly the system converges:

κ = |FXI(t+1) − 1| / |FXI(t) − 1|

Interpretation:

- κ < 1 → stable contraction toward equilibrium.
- κ ≈ 0 → very fast recovery.
- κ ≥ 1 → no convergence; possible instability.

The simulator computes κ at every step to evaluate operator efficiency.

### 17.5 Relationship Between FXI and Δ
Although FXI and Δ are distinct, they interact indirectly:

- scenario shocks can change Δ → which may push FXI away from 1,
- strong operator correction on FXI may, over time, reduce Δ,
- but certain Δ distortions may persist even when FXI ≈ 1.

This interplay is crucial:  
FXI is the **global indicator**, while Δ captures **structural shape**.

### 17.6 Local vs Global Stability
Operators can behave differently in different regions:

- **Local stability**: κ < 1 near equilibrium.  
- **Global stability**: κ < 1 across the entire FXI domain.  
- **Semi-stable operators**: stable near 1 but unstable at extremes.

The simulator helps reveal these behaviours through trajectories and diagnostics.

### 17.7 Noise and Structural Sensitivity
Stochastic scenarios reveal deeper properties:

- sensitivity of \(E\) to small perturbations,
- resilience under noise accumulation,
- threshold behaviours when FXI crosses critical levels.

This helps in determining whether an operator is robust or fragile under real-world uncertainty.

These mathematical notes provide conceptual guidance for interpreting FRE
simulation results and designing new operators.

---

## 18. Examples of Custom Operators

This section provides practical examples of how to define custom corrective
operators \(E\) within the FRE Simulator. These templates demonstrate different
behavioural profiles and can be used as starting points for new operator
designs.

### 18.1 Linear Operator
A simple proportional correction rule:

FXI(t+1) = 1 + α · (FXI(t) − 1)

Where:
- α controls correction strength,
- 0 < α < 1 ensures contractive behaviour,
- α close to 0 results in slow convergence,
- α close to 1 results in minimal correction.

This operator is useful for baseline testing.

### 18.2 Nonlinear (Curved) Operator
A curved operator provides stronger correction far from equilibrium while being
gentler near FXI = 1:

FXI(t+1) = 1 + α · (FXI(t) − 1)³

Key properties:
- very weak correction for small deviations,
- extremely strong correction for large deviations,
- may introduce overshoot or oscillation if α is large.

This operator is suitable for exploring nonlinear stabilization regimes.

### 18.3 Saturating Operator
A saturating operator flattens out when FXI grows too large:

FXI(t+1) = 1 + α · tanh(β · (FXI(t) − 1))

Where:
- α sets overall correction intensity,
- β controls sensitivity to deviation,
- tanh prevents extreme corrections and saturates at ±1.

This operator is useful for testing stability in extreme regions.

### 18.4 Adaptive Operator
An adaptive operator changes correction strength depending on the size of the
deviation:

Let d = |FXI(t) − 1|

If d < τ:
  FXI(t+1) = 1 + α₁ · (FXI(t) − 1)

Else:
  FXI(t+1) = 1 + α₂ · (FXI(t) − 1)

Where:
- α₁ < α₂,  
- τ is the threshold separating low- and high-deviation regimes.

This operator simulates adaptive risk control similar to real-world systems.

### 18.5 Stochastic Operator
A stochastic operator introduces controlled randomness:

FXI(t+1) = 1 + α · (FXI(t) − 1) + ε

Where:
- ε is a noise term drawn from a distribution (e.g., Normal(0, σ)).

This operator is useful for Monte Carlo simulations and operator robustness
testing.

### 18.6 Implementation Notes
To define a custom operator in the simulator:
- create a new class in `operators.py`,
- implement an `apply(fxi_value)` method,
- optionally implement a `kappa(prev, next)` method,
- expose tunable parameters via the constructor.

These examples provide a practical foundation for building a wide range of
corrective operators tailored to specific system behaviour.

---

## 19. Examples of Custom Scenarios

This section demonstrates how to construct custom scenarios that introduce
external shocks, parameter changes, or stochastic disturbances into the FRE
simulation. Scenarios are the primary way to test system resilience under
stress conditions.

### 19.1 Single-Step Shock
A simple shock applied at a specific time step:

If t = t₀:
  qp ← qp + shock_amount

Example use cases:
- sudden liquidity withdrawal,
- structural rebalancing,
- isolated stress event.

This is the most basic form of deterministic scenario.

### 19.2 Multi-Step Progressive Shock
A sequence of shocks applied over several steps:

For t in [t₁, t₂]:
  qf ← qf · (1 − α)

Where α controls the intensity of each step.

Useful for:
- modelling gradual stress buildup,
- slow deterioration of feedback mechanisms,
- staged liquidity drainage.

### 19.3 Parameter Shift Scenario
A discrete regime change:

If t = t₀:
  q ← new_value
  w ← new_value

This models:
- policy changes,
- regime switching,
- structural parameter updates.

### 19.4 Oscillating Scenario
A scenario that introduces periodic behaviour:

qp ← qp + A · sin(ω · t)

Where:
- A is amplitude,
- ω is frequency.

Useful for:
- cyclical stress patterns,
- periodic demand cycles,
- oscillatory feedback testing.

### 19.5 Stochastic Shock Scenario
Random disturbances applied at every step:

qp ← qp + ε  
Where ε ~ Normal(0, σ)

Or more generally:

state_variable ← state_variable + noise(t)

Useful for:
- Monte Carlo simulations,
- random volatility tests,
- noise sensitivity evaluation.

### 19.6 Composite Scenario
A multi-layer scenario combining deterministic and stochastic components:

- deterministic shock at t = 5,
- stochastic noise from t = 5 to 20,
- parameter shift at t = 20,
- recovery phase afterwards.

This creates realistic multi-phase stress tests.

### 19.7 Implementation Notes
To implement a custom scenario:
- create a new class in `scenarios.py`,
- implement an `apply(state, t)` method,
- modify qp, qf, q, w, u, Δ, or FXI as required,
- optionally log scenario events for diagnostics.

These examples provide a flexible foundation for modelling a wide variety of
stress conditions in FRE Simulator V2.0.

---

## 20. Export & Data Handling

The FRE Simulator provides flexible tools for exporting time-series data,
diagnostics, and visual outputs generated during simulations. This enables
external analysis, reproducibility, reporting, and integration with other
research pipelines.

### 20.1 Exportable Data Types

The simulator can export multiple categories of information:

- **FXI trajectory** — full time series of FXI(t).
- **Δ trajectory** — deviation Δ(t) over time.
- **Structural state history** — qp, qf, q, w, u at each step.
- **Stability zones** — stable, stressed, or critical labels.
- **κ (contractivity) values** — step-by-step κ diagnostics.
- **Scenario event log** — all shocks and parameter changes.
- **Breach information** — step and type of any capacity violation.

These data sets can be saved for audit, backtesting, or machine learning input.

### 20.2 Export Formats

The simulator supports several standard export formats:

- **CSV** — for tabular time-series analysis.
- **JSON** — for structured, hierarchical data.
- **PNG** — for visual plots (FXI, Δ, stability zones).
- **TXT** — lightweight plain-text export (optional).
- **Pickle** — raw Python object serialization (for reproducibility).

All exports are compatible with Python, R, MATLAB, Julia, and data science toolkits.

### 20.3 Visualization Export

Plots generated by `visualization.py` (FXI, Δ, stability zones) can be saved
automatically or on demand. Typical usage:

- exporting PNG snapshots for reports,
- saving visualization results during batch simulations,
- comparing operator behaviour across runs.

Visualization export ensures stability regimes and trajectories are documented.

### 20.4 Directory Structure for Outputs

Recommended structure for exported data:

exports/
├── runs/
│   ├── run_001/
│   │   ├── fxi.csv
│   │   ├── delta.csv
│   │   ├── stability_zones.csv
│   │   ├── scenario_log.json
│   │   └── plots/
│   │       ├── fxi.png
│   │       ├── delta.png
│   │       └── stability_zones.png
│   └── run_002/
│       └── ...
└── batch_summary.json

This structure helps maintain clarity when running multiple experiments.

### 20.5 Data Handling for Large Simulations

For long horizons or Monte Carlo experiments:

- data can be streamed to disk instead of held in memory,
- visualization may be skipped for speed,
- state history can be stored with reduced precision.

These options ensure efficiency for large-scale runs.

### 20.6 Reproducibility

Every export should include:

- random seed (if used),
- operator parameters,
- scenario configuration,
- simulation horizon,
- software version.

This guarantees that simulation results can be reproduced exactly.

Export and data-handling features make the FRE Simulator suitable for research,
backtesting, benchmarking, and long-term structural risk analysis.

---

## 21. Performance Notes

This section outlines the performance characteristics of the FRE Simulator,
including runtime considerations, efficiency guidelines, and recommended
strategies for optimizing large-scale simulations.

### 21.1 Computational Complexity

The simulator is lightweight by design.  
Core operations involve:

- simple arithmetic for Δ and FXI updates,
- scenario event application,
- stability and κ evaluation.

Typical complexity per step is **O(1)**, making the entire simulation **O(T)**,
where T is the horizon.

### 21.2 Memory Usage

Memory consumption depends primarily on:

- whether full state history is stored,
- size of exported data,
- number of parallel simulations.

For standard runs (T = 1000), memory usage is minimal.  
For large Monte Carlo experiments, users may disable:

- full state logging,
- stability zone traces,
- visualization caching,

to reduce footprint.

### 21.3 Speed Guidelines

Typical performance on standard CPU hardware:

- 10⁴ steps: < 0.1 seconds  
- 10⁵ steps: ~1 second  
- 10⁶ steps: a few seconds  

Speed varies based on Python implementation and enabled diagnostics.

### 21.4 Optional Vectorization

While FRE Simulator V2.0 is loop-based for clarity, users may speed up execution
by:

- replacing scalar operations with NumPy vectorized code,
- precomputing scenario shocks,
- disabling diagnostics during batch runs.

These optimizations can significantly accelerate large experiments.

### 21.5 Parallelization

For bulk simulations or operator benchmarking:

- run multiple simulations in parallel using multiprocessing,
- assign independent runs to separate worker processes,
- aggregate results asynchronously.

Since runs are independent, parallelization scales almost linearly.

### 21.6 Visualization Performance

Visualization is typically the slowest part of the workflow because:

- plotting Δ, FXI, and zones requires rendering,
- high-resolution PNG export can be expensive.

Performance tips:

- disable plotting during batch runs,
- reduce sampling frequency for long simulations,
- generate plots only after aggregation.

### 21.7 I/O Considerations

When exporting data:

- writing CSV for every step can become a bottleneck,
- batching writes (every N steps) improves performance,
- binary formats (pickle) are significantly faster than JSON or CSV.

### 21.8 Future Optimizations

Planned improvements for future versions:

- JAX/NumPy acceleration,
- vectorized operator libraries,
- streaming loggers for constant-memory runs,
- GPU-optional kernels for extremely large-scale tests.

These notes help users run simulations efficiently, especially when working with
large horizons, Monte Carlo studies, or operator benchmarking workloads.

---

## 22. Roadmap for FRE-Simulator V2.1+

This roadmap outlines the planned enhancements and future development steps for
the FRE Simulator. These upgrades will expand analytical capabilities, improve
performance, and align the simulator more closely with the evolving FRE-2.0
mathematical specification.

### 22.1 Operator Benchmarking Framework
A dedicated module for comparing corrective operators under:
- identical scenarios,
- controlled perturbations,
- long-horizon stress sequences.

This framework will quantify operator strength, stability, and robustness.

### 22.2 Scenario Generator Library
Automated generation of:
- stochastic disturbances,
- parameter sweeps,
- multi-phase composite shocks,
- Monte Carlo scenario batches.

This will simplify large-scale resilience testing.

### 22.3 High-Performance Kernel (NumPy / JAX)
Introduce a vectorized execution path:
- 10–100× speed-up for long horizons,
- GPU-optional acceleration via JAX,
- streaming state computation with constant memory.

This will make the simulator suitable for industrial-scale workloads.

### 22.4 Distributed Simulation Engine
Infrastructure for:
- running thousands of simulations in parallel,
- cluster-based batch execution,
- distributed operator benchmarking.

This enables population-based analysis of operator performance.

### 22.5 Extended Visualization Tools
Improvements include:
- multi-trajectory comparative charts,
- contractivity heatmaps,
- FXI/Δ phase diagrams,
- interactive stability maps.

These expansions enhance exploratory analysis and research workflows.

### 22.6 Configurable Export Pipelines
Customizable export templates supporting:
- run metadata,
- operator signatures,
- scenario descriptors,
- aggregated batch results.

Designed for integration with external research tools and reporting systems.

### 22.7 Plugin Architecture
A modular system for adding:
- custom operators,
- custom scenarios,
- alternative evolution models.

This ensures long-term extensibility of the FRE Simulator ecosystem.

### 22.8 Formal Verification Hooks
Framework additions for:
- validating operator properties (continuity, boundedness, monotonicity),
- checking domain-specific invariants,
- verifying admissibility across the entire evolution cycle.

This brings the simulator closer to its formal mathematical foundations.

### 22.9 Integration With FRE-2.0 Specification
As the FRE theory evolves, the simulator will receive:
- updated evolution rules,
- new structural variables,
- refined zone thresholds,
- expanded operator classes.

The simulator roadmap ensures alignment with the broader Flexionization model.

This roadmap defines the long-term direction of FRE-Simulator development and
sets the foundation for future versions beyond V2.1.
