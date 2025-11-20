# FRE Simulator V2.0  
### Flexionization Risk Engine — Simulation Framework

FRE Simulator V2.0 provides a complete and deterministic execution environment for the  
**Flexionization Risk Engine (FRE)**.  
It implements all FRE 2.0 structural dynamics, corrective operators, scenarios, and  
diagnostic tools in a modular Python package.

The simulator is designed for:

- research and experimentation,
- stress testing,
- validation of FRE models,
- algorithmic development,
- reproducible structural analysis.

Full documentation:  
📄 `docs/FRE-V2.0-Simulator-Documentation.md`


---

## Features

- Full FRE 2.0 evolution loop implementation  
- Modular operators, scenarios, and state model  
- Deterministic execution and reproducible runs  
- Built-in stress test support  
- Visualization tools for FXI, Δ, κ and stability zones  
- Test suite for engine and operator validation  
- Editable installation for development  
- Compatible with Python 3.9+


---

## Installation

Clone the repository and install the simulator:

```bash
pip install -e .
```

Or install all dependencies explicitly:

```bash
pip install -r requirements.txt
```


---

## Quickstart Example

```python
from fre_simulator.state import State
from fre_simulator.operators import DefaultOperator
from fre_simulator.scenarios import EmptyScenario
from fre_simulator.engine import Simulator

state = State(fxi=1.12, delta=0.24)
operator = DefaultOperator()
scenario = EmptyScenario()

sim = Simulator(
    initial_state=state,
    operator=operator,
    scenario=scenario,
    horizon=20
)

result = sim.run()

print(result.fxi_series)
print(result.delta_series)
print(result.zones)
```

For a full working example, see:

📌 `example_simulation.py`


---

## Project Structure

```
FRE-simulator/
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── requirements.txt
├── example_simulation.py
├── run_tests.py
├── docs/
│   └── FRE-V2.0-Simulator-Documentation.md
├── src/
│   └── fre_simulator/
│       ├── state.py
│       ├── operators.py
│       ├── scenarios.py
│       ├── engine.py
│       └── visualization.py
└── tests/
    └── test_engine.py
```


---

## Running Tests

Run all internal validation tests:

```bash
pytest
```

The suite ensures that operator logic, state transitions, contractivity,  
and stability zone classification remain consistent with FRE 2.0.


---

## Documentation

The full technical documentation is available in:

```
docs/FRE-V2.0-Simulator-Documentation.md
```

It includes:

- theoretical reference  
- module-level descriptions  
- evolution loop details  
- visualization tools  
- stress test examples  
- development notes  


---

## License

MIT License.  
See the `LICENSE` file for details.

---

---

## Version 2.0 — Implementation Notes

This section summarizes how the FRE Simulator V2.0 implements the
structural dynamics defined in the official FRE 2.0 mathematical specification.

### ✔ Deterministic Structural Evolution
All transitions follow the formal rule:

\[
\Delta_{t+1} = E(\Delta_t)
\]

with optional scenario modification:

\[
\Delta'_t = S_t(\Delta_t)
\]

No randomness, branching, or heuristic overrides are used.

### ✔ Corrective Operator E⃗
The DefaultOperator implements the canonical contraction rule described in the
specification.  
All corrections are:
- bounded,
- continuous,
- monotone,
- equilibrium-seeking.

### ✔ FXI & Stability Zones
FXI is recomputed at each step and used to classify the state into:
- critical,
- stressed,
- stable,
- compressed zones.

The definitions match those in the official FRE 2.0 Specification (PDF/MD).

### ✔ Strict Admissibility
All deviation updates remain inside the admissible domain ∂D.  
Boundedness constraints follow the FRE 2.0 model exactly.

### ✔ Stress Test Compatibility
The simulator is fully compatible with the official Stress Test Suite
(Levels 1–10) without any modifications to code or operators.

### ✔ No Business Logic
The simulator contains **only** structural dynamics.  
No finance-specific, liquidation, margin-call, or risk heuristics exist in code.

This ensures that FRE remains a **pure structural model** exactly as defined by
the formal theory.

---

## Author

**Maryan Bogdanov**  
Flexionization Research  
2025
