# Flexionization Risk Engine (FRE) — Version 2.0  
### Official Repository • Specification • Simulator • Test Suite

The **Flexionization Risk Engine (FRE) V2.0** is a multidimensional, fully deterministic  
risk-control framework based entirely on **internal structural dynamics**, without reliance  
on volatility triggers, external heuristics, or discontinuous liquidation mechanisms.

This repository contains the complete FRE 2.0 package:

- **Mathematical Specification (PDF / LaTeX / MD)**
- **FRE Simulator V2.0 (Python)**
- **Comprehensive Stress Test Suite (Levels 1–10)**
- **Documentation and development notes**
- **Zenodo DOI references for archival publication**

FRE 2.0 defines stability, equilibrium, and corrective behavior using only:
- the 5-dimensional deviation vector Δ⃗,
- the equilibrium indicator FXI,
- the vector corrective operator E⃗,

ensuring continuous, bounded, and contracting structural evolution across financial and computational systems.

---

- [Repository Structure](#repository-structure)
- [Documentation](#documentation)
- [Zenodo & DOI References](#zenodo--doi-references)
- [FRE 2.0 Model Overview](#fre-20-model-overview)
- [FRE Simulator V2.0](#fre-simulator-v20)
- [Stress Test Suite](#stress-test-suite-levels-110)
- [Installation & Usage](#installation--usage)
- [Versioning](#versioning)
- [License](#license)
- [Author & Contact](#author--contact)

---

## Repository Structure

The FRE V2.0 repository is organized into four core components:

```
FRE-V2.0/
├── FRE-Risk-Engine-V2.0-LaTeX.pdf        # Full mathematical specification (official)
├── FRE-Risk-Engine-V2.0-Specification.md # Markdown specification (GitHub-friendly)
├── FRE-simulator/                        # FRE Simulator V2.0 (Python package)
│   ├── README.md                         # Simulator documentation
│   ├── docs/                             # Simulator-specific documentation
│   │   ├── FRE-V2.0-Simulator-Documentation.md
│   │   └── FRE-2.0-Test-Suite.md
│   ├── src/fre_simulator/                # Core engine implementation
│   ├── example_simulation.py             # Reference example
│   └── tests/                            # Automated validation tests
└── docs/                                 # (Optional) High-level FRE documentation
```

Each component corresponds directly to the FRE 2.0 architecture:

- **Specification:** theoretical foundation and formal model.  
- **Simulator:** executable implementation of FRE structural dynamics.  
- **Test Suite:** verification of stability, contraction, stress behavior, and domain edge cases.  

---

## Documentation

FRE V2.0 includes three layers of official documentation:

### **1. Mathematical Specification (Primary Source)**
📄 **FRE-Risk-Engine-V2.0-LaTeX.pdf**  
The complete academic specification of FRE 2.0, including:
- multidimensional deviation model (Δ⃗),
- equilibrium indicator (FXI),
- corrective operator (E⃗),
- dynamics and stability theorems,
- critical scenarios and admissibility conditions,
- full simulation framework definition.

This is the authoritative reference for all FRE implementations.

---

### **2. Markdown Specification**
📄 **FRE-Risk-Engine-V2.0-Specification.md**  
A GitHub-optimized version of the specification.  
Contains the same structure, definitions, and formulas as the LaTeX document.

---

### **3. Simulator Documentation**
📄 `FRE-simulator/docs/FRE-V2.0-Simulator-Documentation.md`  
Covers:
- State, Operator, Scenario, Engine modules  
- evolution loop breakdown  
- visualization tools  
- structure of trajectories  
- example experiments  

📄 `FRE-simulator/docs/FRE-2.0-Test-Suite.md`  
The complete stress-testing suite for FRE 2.0 (Levels 1–10).

Together, these documents form the full FRE V2.0 system description.

---

## Zenodo & DOI References

All FRE 2.0 materials are archived and published through **Zenodo** for long-term scientific access.  
Each component of the Flexionization framework has its own DOI:

### **Core Theoretical Works**
- **Flexionization Theory V1.5**  
  DOI: **10.5281/zenodo.17618947**

- **Flexion-Immune Model V1.1**  
  DOI: **10.5281/zenodo.17624206**

- **Flexionization Risk Engine (FRE) V1.1**  
  DOI: **10.5281/zenodo.17628118**

### **FRE 2.0 Publication**
Once the FRE 2.0 specification and simulator are published,  
the updated DOI will be added here for citation and archival reference.

These DOIs ensure:
- scientific traceability,  
- verifiable versioning,  
- permanent accessibility of FRE documents.  

---

## FRE 2.0 Model Overview

FRE Version 2.0 defines a **multidimensional, deterministic, and continuous** risk–control
framework based entirely on internal structural dynamics.

At its core, FRE 2.0 consists of three fundamental components:

### **1. Deviation Vector (Δ⃗ ∈ R⁵)**
A five–dimensional structural deviation:
- Δm — margin deviation  
- ΔL — exposure/limit deviation  
- ΔH — hedging & liquidity deviation  
- ΔR — risk–parameter deviation  
- ΔC — capital deviation  

This vector represents the full internal imbalance of a system.

---

### **2. Equilibrium Indicator (FXI)**
A scalar function measuring structural alignment:
- **FXI > 1** → expanded/unstable state  
- **FXI < 1** → compressed/overconservative state  
- **FXI = 1** → structural symmetry  

FXI determines the *direction* of corrective movement.

---

### **3. Corrective Operator (E⃗)**
A vector mapping prescribing the next-step target deviation:

\[
\Delta_{t+1} = E(\Delta_t)
\]

E⃗ is:
- continuous  
- bounded  
- monotonic  
- contraction–seeking  
- equilibrium–aligned  

This operator ensures that all admissible trajectories converge toward equilibrium.

---

Together, these components define a structural, volatility–independent model with:
- no discontinuous liquidations,  
- no heuristic overrides,  
- guaranteed bounded corrections,  
- global convergence properties.

FRE 2.0 forms the theoretical foundation for the simulator and test suite included in this repository.

---

## FRE Simulator V2.0

The FRE Simulator V2.0 provides a complete execution environment for the structural
dynamics defined in the FRE 2.0 specification.  
It is a fully deterministic, reproducible Python framework implementing:

- deviation evolution (Δ⃗ₜ₊₁ = E⃗(Δ⃗ₜ)),  
- FXI evaluation,  
- bounded corrections,  
- stability zone classification,  
- stress-test scenarios,  
- trajectory recording and visualization.

The simulator is located in:

```
FRE-simulator/
```

### Key Features
- Modular architecture (State, Operators, Scenarios, Engine)  
- Deterministic execution and reproducible experiments  
- Built-in stress-testing support (Levels 1–10)  
- Visualization tools for Δ⃗, FXI, κ, and stability zones  
- Automated validation tests (`pytest`)  
- Reference example: `example_simulation.py`

### Simulator Documentation
Full documentation is available in:

- `FRE-simulator/docs/FRE-V2.0-Simulator-Documentation.md`  
- `FRE-simulator/docs/FRE-2.0-Test-Suite.md`

These documents describe module-level behavior, evolution rules,  
stress-test specifications, and development guidelines.

---

## Stress Test Suite (Levels 1–10)

FRE 2.0 includes a complete, reproducible **10-level stress test suite**, designed to validate  
structural stability, contraction behavior, and robustness under extreme internal conditions.

All tests are defined in:

```
FRE-simulator/docs/FRE-2.0-Test-Suite.md
```

### Stress Levels Overview

- **Level 1 — Soft Contraction**  
  Normal structural behavior near equilibrium.

- **Level 2 — Mild Expansion / Compression**  
  Basic deviation perturbations.

- **Level 3 — Critical FXI Conditions**  
  Extreme expanded/compressed FXI values.

- **Level 4 — Single-Component Stress**  
  Δm, ΔL, ΔH, ΔR, or ΔC near boundary.

- **Level 5 — Multi-Component Stress**  
  Coordinated stress across multiple deviation components.

- **Level 6 — Domain Edge Trajectories**  
  Tests admissibility and bounded corrections on ∂D.

- **Level 7 — High-Intensity Structural Shifts**  
  Rapid deviation changes approaching structural limits.

- **Level 8 — Domain Shifts**  
  Sudden changes in deviation space parameters.

- **Level 9 — Slow Drift**  
  Nearly-flat FXI curves with micro-movement.

- **Level 10 — Gaussian Chaos / Stochastic Drift**  
  Randomized structural noise with strict boundedness.

### Verification Criteria
Each level validates:

- FXI stability envelope  
- Δ-norm contraction  
- absence of divergence  
- no direction reversal  
- bounded operator behavior  
- domain admissibility  
- deterministic reproducibility  

The Stress Test Suite ensures that any FRE implementation remains consistent with  
the formal specification under all admissible conditions.

---

## Installation & Usage

The FRE Simulator V2.0 is implemented in Python and runs on any standard environment  
(Python 3.9+). No GPUs or external services are required.

### Installation

Clone the repository and install the simulator:

```bash
pip install -e FRE-simulator/
```

Or install dependencies explicitly:

```bash
pip install -r FRE-simulator/requirements.txt
```

### Quickstart Example

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

### Running Tests

To execute all built-in validation tests:

```bash
pytest
```

The test suite checks:
- operator and state consistency,  
- stability zone classification,  
- contractivity behavior,  
- deterministic evolution,  
- stress-test reproducibility.

The simulator is ready for use immediately after installation.

---

## Versioning

This repository follows a clear versioning structure aligned with the evolution of  
the Flexionization Risk Engine.

### **FRE Version 2.0 — Current Stable Release**
Includes:
- full mathematical specification (PDF/LaTeX/MD),
- FRE Simulator V2.0,
- complete Stress Test Suite (Levels 1–10),
- documentation and validation materials.

This version is fully validated and serves as the **reference implementation**.

---

### **Future Versions**
- **FRE 2.1 (Matrix Interaction Model)** — planned, not under active development  
- **FRE 3.x** — long-term research roadmap  

All future versions will extend the current structural model while maintaining  
strict backward consistency with FRE 2.0 fundamentals.

---

### **Archival & Scientific Traceability**
- All core documents are published on **Zenodo** with permanent DOIs.  
- Each new major version will receive its own DOI.  
- Version numbers apply jointly to both the **specification** and the **simulator**  
  to ensure synchronized evolution.

This versioning framework keeps FRE scientifically consistent, traceable, and reproducible.

---

## License

All code included in the FRE Simulator V2.0 is released under the **MIT License**,  
allowing full use in research, engineering, financial systems, DeFi protocols, and  
commercial applications, provided that proper attribution is preserved.

See the file:

```
FRE-simulator/LICENSE
```

The mathematical specification and technical documentation (PDF/MD) are released  
under **CC-BY 4.0**, permitting reuse, distribution, and adaptation with required citation.

This dual-license structure ensures:
- open scientific accessibility,  
- compatibility with commercial and open-source software,  
- proper attribution for academic publications.

---

## Author & Contact

**Maryan Bogdanov**  
Flexionization Research — Independent Researcher  
Email: **m7823445@gmail.com**

For scientific collaboration, engineering integration, or research inquiries related  
to the Flexionization Risk Engine (FRE), Flexionization Theory, or related frameworks  
(NGT, FCS, Flexion-Immune Model), please reach out using the contact above.

Publication profile (Zenodo):  
https://zenodo.org/search?page=1&size=20&q=Maryan%20Bogdanov

All FRE-related materials are part of the broader **Flexionization Research Program**,  
focused on deterministic structural dynamics, stable risk-control systems, and  
next-generation financial/robotic architectures.
