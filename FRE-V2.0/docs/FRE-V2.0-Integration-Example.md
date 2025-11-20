# FRE V2.0 — Integration Example  
### Full End-to-End Example: External System → FRE → Structural Output

This document provides a complete, real-world integration example showing how an  
external system (NGT, CeFi, DeFi, risk daemon, backend service, etc.) interacts  
with **FRE Simulator V2.0** using the official JSON and Python interfaces.

The purpose of this example is to demonstrate how to embed FRE into  
real production architectures while keeping FRE a pure structural engine.

---

# 1. External System State (Example)

Suppose an external system (e.g., DeFi protocol, CeFi exchange or NGT controller)  
has the following internal structural state:

```
liquidity_pressure = 0.31
reserve_imbalance = 0.18
cycle_tension     = 0.42
```

This is *domain-specific* data.  
FRE must NOT see these variables directly.

We compress them into FRE-compatible inputs.

---

# 2. Adapter: External → FRE Input

The adapter converts system variables into:

- **FXI₀** — structural equilibrium indicator  
- **Δ₀** — deviation magnitude  

Example mapping:

```python
def compress_to_fre_inputs(liquidity_pressure, reserve_imbalance, cycle_tension):
    FXI0 = 1 + (reserve_imbalance * 0.45)
    Delta0 = abs(liquidity_pressure * 0.6 + cycle_tension * 0.4)
    return FXI0, Delta0
```

This compression is **purely external**.  
FRE remains clean and domain-independent.

---

# 3. JSON Request (Canonical FRE Format)

The external system sends the FRE request:

```json
{
  "fxi": 1.081,
  "delta": 0.346,
  "horizon": 20,
  "scenario": "empty",
  "params": {
    "kappa": 0.4
  }
}
```

Scenario `"empty"` means:  
**no external shocks — pure structural evolution.**

---

# 4. FRE Python Execution

Backend or risk daemon calls FRE:

```python
from fre_simulator.state import State
from fre_simulator.engine import Simulator
from fre_simulator.operators import DefaultOperator
from fre_simulator.scenarios import EmptyScenario


def run_fre_simulation(fxi0, delta0, horizon=20, scenario_name="empty"):

    if scenario_name == "empty":
        scenario = EmptyScenario()
    else:
        raise NotImplementedError(f"Scenario '{scenario_name}' not integrated.")

    state = State(fxi=fxi0, delta=delta0)
    operator = DefaultOperator()

    simulator = Simulator(
        initial_state=state,
        operator=operator,
        scenario=scenario,
        horizon=horizon
    )

    return simulator.run()
```

This is the **canonical integration call**.

---

# 5. FRE Output (JSON)

Example FRE output:

```json
{
  "fxi_series": [
    1.0810, 1.0430, 1.0172, 1.0068, 1.0027
  ],
  "delta_series": [
    0.346, 0.138, 0.055, 0.022, 0.009
  ],
  "zones": [
    "critical", "stressed", "stressed", "stable", "stable"
  ],
  "kappa_series": [
    null, 0.4, 0.4, 0.4, 0.4
  ],
  "meta": {
    "horizon": 20,
    "scenario": "empty",
    "converged": true,
    "version": "FRE-2.0"
  }
}
```

---

# 6. Interpretation (Adapter → External System)

External system interprets the output:

| FRE Result | Meaning | External System Reaction |
|-----------|----------|--------------------------|
| FXI → 1   | system self-normalizes | normal mode |
| Δ → 0     | internal tension dissolves | no intervention needed |
| zone = stressed | internal imbalance | activate mild risk controls |
| zone = critical | severe structural instability | activate strong protection |

### Example interpretation logic:

```python
def interpret_fre_output(result):
    zone = result["zones"][-1]
    if zone == "critical":
        return "activate_protection_mode"
    if zone == "stressed":
        return "apply_soft_stabilization"
    return "system_normal"
```

---

# 7. End-to-End Flow Summary

```
External State (liquidity, reserves, tension)
             ↓
         Adapter
  (compression into FXI₀, Δ₀)
             ↓
      FRE JSON Request
             ↓
      FRE Simulator V2.0
             ↓
      FRE JSON Response
             ↓
         Adapter
 (interpretation + mapping)
             ↓
 External Actions / Risk Logic
```

Important:  
**FRE never sees any business logic.  
Business logic never changes FRE.**  
Only compression and interpretation layers change.

---

# 8. What This Example Demonstrates

✓ How to turn protocol data into FRE inputs  
✓ How to call FRE through Python interface  
✓ How to use JSON format  
✓ How to interpret structural results  
✓ How to create real-world stabilization logic  
✓ How FRE acts as a pure structural engine

---

# 9. Status

This example completes the official FRE 2.0 integration layer and  
can be used as a template for:

- NGT  
- CeFi exchanges  
- AMM/DeFi protocols  
- liquidity controllers  
- risk systems  
- forecasting engines
