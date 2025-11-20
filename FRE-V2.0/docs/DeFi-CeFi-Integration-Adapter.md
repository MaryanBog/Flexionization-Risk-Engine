# DeFi / CeFi Integration Adapter  
### FRE 2.0 → Structural Risk Mapping for Exchanges, AMMs, Lending Protocols

This document defines how **FRE Version 2.0** integrates into  
**centralized exchanges (CeFi)** and **decentralized finance protocols (DeFi)**  
as a structural stability engine.

FRE 2.0 evaluates **internal structural risk**, not market volatility,  
making it compatible with any financial system using reserves, liquidity,  
capital buffers, oracle inputs, or margin mechanics.

---

# 1. Purpose of the Adapter

The DeFi/CeFi Adapter connects three things:

1. **Protocol State** → converts liquidity + reserves into Δ₀ and FXI₀  
2. **FRE Simulator** → predicts structural stability  
3. **Protocol Logic** → reacts to FRE signals

FRE stays **pure mathematics**.  
CeFi/DeFi remain **business logic**.

---

# 2. Mapping DeFi/CeFi State → FRE Input

The adapter converts protocol state variables into FRE structure:

### ✔ FXI₀ — equilibrium indicator  
### ✔ Δ₀ — structural deviation mass

General mapping:

```
FXI₀ = F( reserves, capital_ratio, imbalance_mass, interest_drift )
Δ₀  = G( liquidity_tension, leverage_ratio, utilization, demand_shift )
```

Where:

- **F** — compression of protocol symmetry  
- **G** — compression of structural tension  
- These functions live **in the adapter**, not inside FRE

### Example (simplified):

For a liquidity pool (AMM):

```
FXI₀ = 1 + (reserve_imbalance / α)
Δ₀   = abs(price_curve_tension / β)
```

For CeFi exchange:

```
FXI₀ = 1 + (margin_pressure / C1)
Δ₀   = abs(hedging_gap / C2)
```

For lending protocol:

```
FXI₀ = 1 + (bad_debt_pressure / L1)
Δ₀   = utilization * L2
```

FRE never sees AMM, oracles, pools, or margin accounts —  
it only sees **Δ₀ and FXI₀**.

---

# 3. FRE Simulation Inside the Protocol

Example integration method:

```python
def run_fre_for_protocol(FXI0, Delta0, horizon=20):
    from fre_simulator.state import State
    from fre_simulator.engine import Simulator
    from fre_simulator.operators import DefaultOperator
    from fre_simulator.scenarios import EmptyScenario

    state = State(fxi=FXI0, delta=Delta0)
    sim = Simulator(
        initial_state=state,
        operator=DefaultOperator(),
        scenario=EmptyScenario(),
        horizon=horizon
    )
    return sim.run()
```

This function becomes part of:

- risk daemons  
- liquidation prevention systems  
- rebalancers  
- AMM controllers  
- loan stability monitors  
- CeFi treasury bots  

---

# 4. FRE Output → Protocol Actions

Protocols use FRE’s structural diagnosis to refine risk decisions.

| FRE Output | Meaning | Protocol Action |
|-----------|----------|----------------|
| FXI > 1.05 | expanded instability | tighten liquidity / raise collateral |
| FXI < 0.95 | compression instability | reduce penalties / release liquidity |
| Δ rising | structural tension | reduce leverage / slow growth |
| stressed zone | systematic imbalance | activate stabilization logic |
| critical zone | severe | initiate full protection mode |

Examples:

### ✔ AMM
- adjust swap fees dynamically based on structural pressure  
- increase liquidity amplification when Δ high  

### ✔ Lending Protocol
- automate collateral-factor adjustments  
- pre-emptively identify bad debt buildup  

### ✔ CeFi Exchange
- tune margin requirements  
- forecast liquidity drain risk  
- stabilize balance sheet  

All actions occur **outside FRE**.

---

# 5. DeFi / CeFi Integration Flow

```
Protocol State
       ↓
DeFi-CeFi Adapter (compression)
       ↓
FXI₀, Δ₀
       ↓
FRE Simulator V2.0 (pure math)
       ↓
FXI(t), Δ(t), Zones
       ↓
DeFi-CeFi Adapter (interpretation)
       ↓
Protocol Risk Logic / Liquidity Logic
```

Two transformations happen **only in the adapter layer**:

1. compression → FRE  
2. interpretation → protocol logic

---

# 6. Version Binding

To ensure compatibility:

```
FRE Version = 2.0.x
```

A protocol must pin the FRE version,  
because 2.1 will introduce interaction matrices and new geometry.

---

# 7. Status

This document defines the **official approach** for integrating FRE V2.0  
into DeFi & CeFi risk-control systems.

Future updates may include:

- advanced scenarios for AMM curves  
- integration templates for margin engines  
- structural oracle specifications  
- multi-stage horizon evaluation  
- on-chain/off-chain hybrid architecture  

FRE remains the **structural core**,  
while the protocols retain all domain-specific logic.
