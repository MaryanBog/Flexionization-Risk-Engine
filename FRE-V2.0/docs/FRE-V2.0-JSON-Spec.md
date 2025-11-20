# FRE V2.0 — JSON Integration Specification  
### Canonical Input/Output Format for External Systems

This document defines the **official JSON data format** for interacting with  
the Flexionization Risk Engine (FRE) Version 2.0.

The specification is designed to be:

- minimal,  
- deterministic,  
- version-stable,  
- compatible with REST, RPC, and message-based systems,  
- easy to embed into DeFi/CeFi protocols, NGT, agents, and risk daemons.

---

# 1. FRE JSON Input Specification

External systems must send data to FRE in the following format:

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

## 1.1 Field Definitions

### `fxi` (float)
Initial equilibrium indicator FXI₀.

### `delta` (float)
Initial structural deviation Δ₀  
(scalar or the norm of the deviation vector in extended versions).

### `horizon` (int)
Number of FRE evolution steps to simulate.

### `scenario` (string)
Name of the FRE scenario to use:

- `"empty"`  
- `"level1_soft"`  
- `"level3_critical"`  
- `"level7_multishift"`  
- `"level10_stochastic"`  
- etc.

The adapter is responsible for scenario mapping.

### `params` (object)
Optional operator parameters.  
Default FRE 2.0 uses:

```json
{ "kappa": 0.4 }
```

---

# 2. FRE JSON Output Specification

FRE returns a deterministic structural trajectory:

```json
{
  "fxi_series": [1.1275, 1.0510, 1.0204, 1.0082],
  "delta_series": [0.2550, 0.1020, 0.0408, 0.0163],
  "zones": ["critical", "stressed", "stressed", "stable"],
  "kappa_series": [null, 0.4, 0.4, 0.4],
  "meta": {
    "horizon": 20,
    "scenario": "empty",
    "converged": true,
    "version": "FRE-2.0"
  }
}
```

## 2.1 Field Definitions

### `fxi_series` (array<float>)
FXI(t) from t=0…horizon.

### `delta_series` (array<float>)
Δ(t) values for each time step.

### `zones` (array<string>)
Stability classifications:

- `"critical"`  
- `"stressed"`  
- `"stable"`  
- `"compressed"`

### `kappa_series` (array<float|null>)
Contraction coefficient at each step.

### `meta` (object)
Additional fields required by external systems:

- `horizon` — number of steps  
- `scenario` — scenario identifier  
- `converged` — did Δ(t) reach near-equilibrium  
- `version` — strict version pinning

---

# 3. Error Format

Any error returned by FRE follows a canonical error format:

```json
{
  "error": {
    "type": "InvalidInput",
    "message": "Delta must be a positive number.",
    "details": {}
  }
}
```

Valid error types:

- `"InvalidInput"`  
- `"UnknownScenario"`  
- `"OperatorError"`  
- `"SimulationError"`  
- `"InternalError"`  

---

# 4. Version Binding

All integrations **must** specify the FRE version used:

```json
"version": "FRE-2.0"
```

This ensures compatibility when FRE 2.1 and 3.x are released.

---

# 5. Usage Examples

## 5.1 Minimal Request

```json
{
  "fxi": 1.05,
  "delta": 0.12,
  "horizon": 10,
  "scenario": "empty"
}
```

## 5.2 Response

```json
{
  "fxi_series": [...],
  "delta_series": [...],
  "zones": [...],
  "kappa_series": [...],
  "meta": {
    "horizon": 10,
    "scenario": "empty",
    "converged": true,
    "version": "FRE-2.0"
  }
}
```

---

# 6. Integration Principles

1. Same input → same output (deterministic).  
2. Input must be validated before simulation.  
3. Scenarios are adapter-resolved.  
4. FRE internal structure must never be modified.  
5. Error format must be respected.  
6. All integrations must be version-pinned.

---

# 7. Status

This JSON specification is the **official format** for  
FRE Version 2.0 integration into external systems.  
It is stable and will remain backward-compatible until FRE 3.x.
