# FRE V2.0 Integration API  
### Structural Risk Engine Interface • Input/Output Specification

This document describes how to integrate the **Flexionization Risk Engine (FRE) V2.0**  
into external systems (NGT, DeFi/CeFi protocols, banking risk stacks, simulators).

FRE 2.0 is a **pure structural engine**. It does not depend on market rules,  
liquidation heuristics, or asset-specific logic. Integration happens through  
clean, deterministic data structures.

---

## 1. High-Level Architecture

External system → **Adapter** → FRE Input → FRE Simulator → FRE Output → External system

Where:

- **Adapter** — converts system-specific state into FRE-compatible input.
- **FRE Simulator** — runs the structural evolution (no business logic inside).
- **Outputs** — structural metrics (FXI, Δ, zones, trajectories).

FRE does *not* make business decisions. It only provides **structural signals**.

---

## 2. Core Input Structure

At API level we use a minimal, implementation-agnostic structure:

```json
{
  "fxi": 1.1275,
  "delta": 0.2550,
  "horizon": 20,
  "scenario": "empty",
  "params": {
    "kappa": 0.4
  }
}
```

### Fields:

- `fxi` — initial equilibrium indicator FXI₀  
- `delta` — initial deviation magnitude Δ₀ (scalar, or norm of Δ⃗)  
- `horizon` — number of evolution steps to simulate  
- `scenario` — name of the scenario (e.g., `"empty"`, `"level3_critical"`, `"level7_multi"`)  
- `params` — optional parameter set (e.g., operator coefficients, κ, bounds)

This structure is sufficient for:

- running deterministic simulations,  
- stress tests,  
- scenario analysis,  
- probing stability zones.

---

## 3. Core Output Structure

The FRE engine returns a trajectory summary:

```json
{
  "fxi_series": [1.1275, 1.0510, 1.0204, ...],
  "delta_series": [0.2550, 0.1020, 0.0408, ...],
  "zones": ["critical", "stressed", "stressed", "stable", ...],
  "kappa_series": [null, 0.4, 0.4, 0.4, ...],
  "meta": {
    "horizon": 20,
    "scenario": "empty",
    "converged": true
  }
}
```

### Fields:

- `fxi_series` — FXI(t) for t = 0…T  
- `delta_series` — Δ(t) or ||Δ⃗(t)||  
- `zones` — structural stability zone per step  
- `kappa_series` — contraction coefficient / operator parameter per step  
- `meta` — horizon, scenario, convergence flags

---

## 4. Python Integration Example

A minimal integration snippet:

```python
from fre_simulator.state import State
from fre_simulator.operators import DefaultOperator
from fre_simulator.scenarios import EmptyScenario
from fre_simulator.engine import Simulator


def run_fre_simulation(fxi, delta, horizon=20, scenario_name="empty"):
    # 1. Map scenario name to FRE scenario
    if scenario_name == "empty":
        scenario = EmptyScenario()
    else:
        raise NotImplementedError(f"Scenario '{scenario_name}' not integrated yet.")

    # 2. Build initial FRE state
    state = State(fxi=fxi, delta=delta)

    # 3. Use default operator (canonical FRE 2.0)
    operator = DefaultOperator()

    # 4. Run simulation
    sim = Simulator(
        initial_state=state,
        operator=operator,
        scenario=scenario,
        horizon=horizon,
    )
    result = sim.run()

    # 5. Map result to generic API format
    return {
        "fxi_series": result.fxi_series,
        "delta_series": result.delta_series,
        "zones": result.zones,
        "kappa_series": result.kappa_series,
        "meta": {
            "horizon": horizon,
            "scenario": scenario_name,
            "converged": result.converged,
        },
    }
```

This function can be used:

- inside backend services,  
- inside NGT agents,  
- in DeFi risk daemons,  
- in off-chain controllers.

---

## 5. JSON-based Integration

For REST / RPC usage, the FRE engine can be wrapped into an HTTP or message-based service.

### Example Request (JSON):

```json
POST /fre/v2/simulate

{
  "fxi": 1.1275,
  "delta": 0.2550,
  "horizon": 20,
  "scenario": "empty",
  "params": {
    "kappa": 0.4
  }
}
```

### Example Response (JSON):

```json
{
  "fxi_series": [1.1275, 1.0510, 1.0204, 1.0082],
  "delta_series": [0.2550, 0.1020, 0.0408, 0.0163],
  "zones": ["critical", "stressed", "stressed", "stable"],
  "kappa_series": [null, 0.4, 0.4, 0.4],
  "meta": {
    "horizon": 4,
    "scenario": "empty",
    "converged": true
  }
}
```

---

## 6. CeFi / DeFi / Banking Adapters (Conceptual)

FRE does not connect directly to exchanges or chains.  
Instead, **adapters** translate external state into FRE initial conditions.

Examples:

### CeFi Adapter:
- reads: positions, collateral, margin, limits  
- computes: FXI₀, Δ₀ from internal state  
- calls FRE with `{fxi, delta, horizon, scenario}`  
- consumes output as structural risk signal.

### DeFi Adapter:
- reads: smart-contract storage, oracle feeds, protocol parameters  
- computes Δ₀ and FXI₀ from structural mass  
- runs FRE for scenario (`level7_defi_stress`, etc.).

### Banking Adapter:
- reads: RWA, EAD, VaR/ES, capital buffers  
- compresses into structural deviation  
- feeds FRE for structural equilibrium analysis.

These adapters live **outside** FRE and respect the pure structural nature of the engine.

---

## 7. Integration Principles

To keep compatibility with FRE 2.0:

1. **No business rules inside FRE**  
   All domain specifics live in the adapter layer.

2. **Deterministic calls only**  
   Same input → same output.

3. **No external randomness**  
   If stochastic scenarios are needed, they must be explicitly controlled.

4. **FXI and Δ are canonical**  
   Do not reinterpret them; use the definitions from the FRE 2.0 Specification.

5. **Version pinning**  
   When integrating, always bind to a specific FRE version: `2.0.x`.

---

## 8. Status

This Integration API describes the **official integration surface** for FRE Version 2.0.  
Future versions (2.1, 3.x) will extend this model, but the core pattern:

> external system → adapter → FRE → structural output

will remain stable.
