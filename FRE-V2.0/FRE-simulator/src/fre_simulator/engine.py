# engine.py
# Core evolution loop for FRE Simulator V2.0
# Applies scenarios, updates FXI via operator E, tracks stability and breaches.

from dataclasses import dataclass, replace
from typing import List, Optional, Any, Dict

from .state import State
from .operators import BaseOperator
from .scenarios import BaseScenario

"""
Engine Module — FRE Simulator V2.0
==================================

This module implements the **core evolution loop** of the Flexionization
Risk Engine (FRE) Version 2.0.  
It defines how the structural deviation Δ⃗ and equilibrium indicator FXI evolve
step-by-step under the corrective operator E⃗ and optional scenario-based shocks.

The FRE evolution loop follows the formal definition from the FRE 2.0
mathematical specification:

    1. Start with initial deviation Δ⃗₀ and FXI₀
    2. Apply external scenario Sₜ         → Δ⃗'ₜ
    3. Apply corrective operator E⃗       → Δ⃗ₜ₊₁
    4. Compute updated FXI(Δ⃗ₜ₊₁)
    5. Classify the current stability zone
    6. Repeat until horizon H

Core Guarantees (from FRE Specification):

- **Determinism:** No randomness is allowed inside the engine.
- **Continuity:** All transitions are continuous functions of the state.
- **Boundedness:** Δ⃗ and FXI remain within the admissible domain ∂D.
- **Contraction:** E⃗ ensures movement toward the equilibrium zone.
- **Predictability:** Results are fully reproducible for all inputs.
- **No liquidation heuristics:** No discontinuous rules or external triggers.

The `Simulator` class defined here serves as the canonical execution environment
used by:

- the official FRE 2.0 example simulation,
- the full Stress Test Suite (Levels 1–10),
- automated validation tests,
- research experiments,
- integration prototypes (NGT, FCS, DeFi/CeFi models).

This module contains no business logic — only pure structural dynamics.
"""

@dataclass
class SimulationResult:
    """
    Structured output of a FRE simulation run.
    """
    fxi_series: List[float]
    delta_series: List[float]
    state_series: List[State]
    kappa_series: List[Optional[float]]
    stability_zones: List[str]
    scenario_events: List[Dict[str, Any]]

    breach_occurred: bool
    breach_step: Optional[int]
    breach_state: Optional[State]
    breach_type: Optional[str]


def _classify_zone(fxi: float, eps1: float, eps2: float) -> str:
    """
    Stability zone classification based on |FXI - 1|.
    Stable:   |FXI - 1| <= eps1
    Stressed: eps1 < |FXI - 1| <= eps2
    Critical: |FXI - 1| > eps2
    """
    dev = abs(fxi - 1.0)
    if dev <= eps1:
        return "stable"
    if dev <= eps2:
        return "stressed"
    return "critical"


def run_simulation(
    initial_state: State,
    operator: BaseOperator,
    scenario: BaseScenario,
    horizon: int,
    config: Optional[dict] = None
) -> SimulationResult:
    """
    Execute FRE structural evolution for a given horizon.

    Steps per iteration t:
        1. Apply scenario to state S(t)
        2. Recompute Δ(t) (from qp, qf) if needed
        3. Compute FXI(t+1) = E(FXI(t))
        4. Update state from new FXI (and Δ)
        5. Classify stability zone
        6. Compute κ
        7. Check capacity constraints (breach detection)
        8. Log state and diagnostics

    Parameters:
        initial_state — starting structural state S0
        operator      — corrective operator E
        scenario      — stress scenario
        horizon       — number of steps
        config        — optional dict with:
            "zone_thresholds": { "eps1": float, "eps2": float }
            "capacity_limits": { "delta": float, "fxi_min": float, "fxi_max": float }

    Returns:
        SimulationResult with full trajectories and diagnostics.
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    cfg = config or {}

    # Stability zone thresholds
    zone_cfg = cfg.get("zone_thresholds", {})
    eps1 = zone_cfg.get("eps1", 0.02)
    eps2 = zone_cfg.get("eps2", 0.10)

    # Capacity limits (fallback to State defaults if provided)
    cap_cfg = cfg.get("capacity_limits", {})
    delta_max = cap_cfg.get("delta", initial_state.DELTA_MAX)
    fxi_min = cap_cfg.get("fxi_min", initial_state.FXI_MIN)
    fxi_max = cap_cfg.get("fxi_max", initial_state.FXI_MAX)

    # Prepare series
    fxi_series: List[float] = []
    delta_series: List[float] = []
    state_series: List[State] = []
    kappa_series: List[Optional[float]] = []
    stability_zones: List[str] = []
    scenario_events: List[Dict[str, Any]] = []

    breach_occurred = False
    breach_step: Optional[int] = None
    breach_state: Optional[State] = None
    breach_type: Optional[str] = None

    # Current state
    state = replace(initial_state)  # copy to avoid mutating caller's object
    state.validate()

    # Record initial point (t=0, before first operator application)
    fxi_series.append(state.fxi)
    delta_series.append(state.delta)
    state_series.append(replace(state))
    kappa_series.append(None)  # κ not defined at t=0
    stability_zones.append(_classify_zone(state.fxi, eps1, eps2))
    scenario_events.append({"t": 0, "type": "init", "info": {}})

    # Evolution loop
    for t in range(1, horizon + 1):
        if breach_occurred:
            # Stop evolution after first breach
            break

        # 1) Apply scenario at step t (using state at t-1)
        before = replace(state)
        state = scenario.apply(state, t)
        after = replace(state)
        if before != after:
            scenario_events.append({
                "t": t,
                "type": "scenario",
                "info": {
                    "before": before,
                    "after": after
                }
            })
        else:
            scenario_events.append({
                "t": t,
                "type": "none",
                "info": {}
            })

        # 2) Recompute Δ(t) from qp, qf (simple placeholder mapping)
        try:
            state.compute_delta()
        except ZeroDivisionError as e:
            breach_occurred = True
            breach_step = t
            breach_state = replace(state)
            breach_type = f"delta-computation-error: {e}"
            break

        # 3) Compute FXI(t+1) via operator E
        prev_fxi = state.fxi
        next_fxi = operator.apply(prev_fxi)

        # Enforce capacity limits on FXI explicitly
        if next_fxi < fxi_min or next_fxi > fxi_max:
            breach_occurred = True
            breach_step = t
            breach_state = replace(state)
            breach_type = "fxi-capacity-breach"
            break

        # 4) Update state from operator result
        state.update_from_operator(next_fxi)

        # 5) Classify stability zone (based on FXI after correction)
        zone = _classify_zone(state.fxi, eps1, eps2)

        # 6) Compute κ
        kappa_value = operator.kappa(prev_fxi, state.fxi)

        # 7) Check Δ capacity
        if abs(state.delta) > delta_max:
            breach_occurred = True
            breach_step = t
            breach_state = replace(state)
            breach_type = "delta-capacity-breach"

        # 8) Store trajectories
        fxi_series.append(state.fxi)
        delta_series.append(state.delta)
        state_series.append(replace(state))
        kappa_series.append(kappa_value)
        stability_zones.append(zone)

    return SimulationResult(
        fxi_series=fxi_series,
        delta_series=delta_series,
        state_series=state_series,
        kappa_series=kappa_series,
        stability_zones=stability_zones,
        scenario_events=scenario_events,
        breach_occurred=breach_occurred,
        breach_step=breach_step,
        breach_state=breach_state,
        breach_type=breach_type,
    )
