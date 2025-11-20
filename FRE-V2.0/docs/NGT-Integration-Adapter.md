# NGT Integration Adapter  
### FRE 2.0 → Next Generation Token (NGT) Structural Link

This document explains how the **Flexionization Risk Engine (FRE) V2.0**  
integrates into the **NGT (Next Generation Token)** system as a structural  
risk-control and stability-guidance core.

NGT is a token designed to follow **deterministic structural dynamics** rather  
than market heuristics. FRE serves as the underlying model that evaluates  
internal deviations and determines the stable/unstable zones of the ecosystem.

---

# 1. Purpose of the Adapter

The NGT Adapter connects **NGT state → FRE input** and  
**FRE output → NGT decisions**.

FRE remains a **pure structural engine**.  
All domain logic stays in NGT.

NGT Adapter performs three tasks:

1. Converts NGT system variables into structural measures (FXI₀, Δ₀).  
2. Runs FRE simulation with a selected horizon and scenario.  
3. Converts the FRE structural output into token-level guidance signals.

---

# 2. NGT → FRE Input Mapping

NGT stores internal structural information.  
Adapter compresses it into the only two FRE-required values:

### ✔ FXI₀ — equilibrium indicator  
### ✔ Δ₀ — deviation magnitude

General mapping:

```
FXI₀ = F( liquidity, supply_demand, volatility_mass, reserve_ratio )
Δ₀  = G( imbalance_mass, cycle_phase, structural tension )
```

Where:

- **F** and **G** are deterministic compression functions.  
- They DO NOT change FRE.  
- They live exclusively inside the NGT Adapter.

**Example simplified mapping:**

```
FXI₀ = 1 + (supply_demand_imbalance / K1)
Δ₀   = abs(structural_pressure / K2)
```

All constants (K1, K2, etc.) belong to NGT, not FRE.

---

# 3. Running FRE from NGT

Adapter calls FRE through a minimal Python interface.

Example:

```python
from fre_simulator.state import State
from fre_simulator.engine import Simulator
from fre_simulator.operators import DefaultOperator
from fre_simulator.scenarios import EmptyScenario

def ngt_run_fre(fxi0, delta0, horizon=20):
    state = State(fxi=fxi0, delta=delta0)
    operator = DefaultOperator()
    scenario = EmptyScenario()

    sim = Simulator(
        initial_state=state,
        operator=operator,
        scenario=scenario,
        horizon=horizon,
    )

    return sim.run()
```

Result: structural trajectory (FXI(t), Δ(t), zones).

---

# 4. FRE Output → NGT Actions

FRE does **not** make decisions.  
NGT decides what to do with FRE’s signals.

The Adapter translates this:

| FRE Output | Meaning | NGT Interpretation |
|-----------|----------|-------------------|
| FXI > 1.05 | system expanded | reduce pressure, activate compression tools |
| FXI < 0.95 | system compressed | activate expansion or stabilizing tools |
| Δ rising | structural tension | apply corrective tokenomics |
| zone = stressed | unstable | enable mild adjustments |
| zone = critical | severe | activate strong stabilization |

### FRE gives a **structural diagnosis**.  
### NGT performs **actions** based on that diagnosis.

---

# 5. How NGT Uses FRE Signals

Examples:

## ✔ Stability Tuning  
Adjust internal parameters depending on FXI/Δ dynamics.

## ✔ Liquidity Shaping  
Increase or reduce on-chain liquidity to stabilize structure.

## ✔ DAO Governance  
Provide FRE-based structural risk reports for automated proposals.

## ✔ Buyback & Burn Triggers  
Use structural deviation instead of market heuristics.

## ✔ Monthly/Weekly Structural Check  
Run horizon=20 or horizon=60 predictions.

NGT becomes **self-stabilizing** because FRE explains  
*структурную форму системы*, а не рыночные шумы.

---

# 6. Full Integration Flow

```
NGT Internal State
        ↓
NGT Adapter (compression)
        ↓
FXI₀, Δ₀
        ↓
FRE Simulator V2.0 (pure structure)
        ↓
FXI(t), Δ(t), Zones, κ
        ↓
NGT Adapter (interpretation)
        ↓
NGT Token Logic / DAO Decisions
```

Two-way transformation happens ONLY in the adapter.  
FRE stays clean and mathematical.

---

# 7. Version Binding

NGT must explicitly use:

```
FRE Version = 2.0.x
```

Future FRE versions (2.1, 3.0) may change:

- deviation geometry,  
- operator mappings,  
- scenario structure.

Binding guarantees NGT stability.

---

# 8. Status

This adapter defines the **official integration path** between  
NGT and FRE Version 2.0.

Future updates may add:

- advanced scenario mapping,  
- multi-horizon predictions,  
- adapter-side smoothing,  
- DAO decision templates.

FRE must always remain the **pure structural layer**,  
while NGT acts as the **token and governance layer**.
