"""
Scenarios Module — FRE Simulator V2.0
=====================================

This module defines the external structural scenarios used in the FRE 2.0
simulation framework. A scenario represents external conditions or shocks
applied to the deviation state Δ during the evolution loop.

Core principles of FRE 2.0 scenarios:

1. Deterministic Shocks:
   All scenario transformations must be deterministic and reproducible.
   No randomness is permitted unless explicitly defined in a controlled
   stress-test (e.g., Level 10 stochastic drift).

2. Structural Consistency:
   A scenario may apply a shift to Δ or FXI, but it must *not* modify the
   corrective operator E⃗ or the FRE dynamics themselves.

3. Bounded Effects:
   Scenario-induced deviations must respect the admissible domain ∂D defined
   in the FRE 2.0 specification.

4. Reproducible Stress Levels:
   Each stress scenario corresponds to a formal level in the FRE 2.0
   Stress Test Suite (Levels 1–10), allowing consistent validation and
   regression testing.

The EmptyScenario provided here applies **no** external shocks and is used for
baseline simulations, including the reference example included with FRE 2.0.
"""

# scenarios.py
# Scenario definitions for FRE Simulator V2.0
# Implements deterministic and stochastic stress scenarios.

from abc import ABC, abstractmethod
from typing import Optional
import random

from .state import State


class BaseScenario(ABC):
    """
    Abstract base class for all FRE scenarios.

    Scenarios modify the structural state S(t) at each time step t.
    The engine will call:

        state = scenario.apply(state, t)

    Convention:
        - scenario modifies state IN-PLACE and returns it
        - if no changes are applied, state is returned unchanged
    """

    @abstractmethod
    def apply(self, state: State, t: int) -> State:
        """Apply scenario logic at time step t."""
        raise NotImplementedError


class EmptyScenario(BaseScenario):
    """
    Scenario that applies no shocks and keeps the system unchanged.
    Used as a baseline / control run.
    """

    def apply(self, state: State, t: int) -> State:
        # no modification
        return state


class SingleStepShockScenario(BaseScenario):
    """
    Single-step shock at time t0.

    Example usage:
        - sudden change of qp (liquidity, exposure)
        - discrete structural event

    Parameters:
        t0          — time step of the shock
        qp_shift    — additive change to qp at t0 (default 0.0)
        qf_shift    — additive change to qf at t0 (default 0.0)
        delta_shift — additive change to Δ at t0 (optional, default 0.0)

    Notes:
        - After modifying qp/qf, delta can be recomputed via state.compute_delta()
          in the engine if needed.
    """

    def __init__(self,
                 t0: int,
                 qp_shift: float = 0.0,
                 qf_shift: float = 0.0,
                 delta_shift: float = 0.0):
        self.t0 = t0
        self.qp_shift = qp_shift
        self.qf_shift = qf_shift
        self.delta_shift = delta_shift

    def apply(self, state: State, t: int) -> State:
        if t == self.t0:
            state.qp += self.qp_shift
            state.qf += self.qf_shift
            state.delta += self.delta_shift
        return state


class ProgressiveShockScenario(BaseScenario):
    """
    Progressive (multi-step) shock on qf across [t_start, t_end].

    Example:
        - gradual tightening/loosening of feedback quantity qf

    Update rule:
        For t_start <= t <= t_end:
            qf ← qf * (1 − alpha)

    Parameters:
        t_start — first step of shock (inclusive)
        t_end   — last step of shock (inclusive)
        alpha   — fraction change per step (0 < alpha < 1)
    """

    def __init__(self, t_start: int, t_end: int, alpha: float):
        if t_end < t_start:
            raise ValueError("t_end must be >= t_start")
        if not (0.0 < alpha < 1.0):
            raise ValueError("alpha must be in (0, 1)")
        self.t_start = t_start
        self.t_end = t_end
        self.alpha = alpha

    def apply(self, state: State, t: int) -> State:
        if self.t_start <= t <= self.t_end:
            state.qf *= (1.0 - self.alpha)
        return state


class StochasticNoiseScenario(BaseScenario):
    """
    Stochastic noise scenario applied to qp at each step.

    Example usage:
        - Monte Carlo noise on primary quantity qp

    Update rule:
        qp ← qp + ε
        where ε ~ Normal(0, sigma)

    Parameters:
        sigma — standard deviation of noise
        seed  — random seed for reproducibility (optional)
    """

    def __init__(self, sigma: float, seed: Optional[int] = None):
        if sigma <= 0:
            raise ValueError("sigma must be positive")
        self.sigma = sigma
        self._rng = random.Random(seed) if seed is not None else random

    def apply(self, state: State, t: int) -> State:
        eps = self._rng.normalvariate(0.0, self.sigma)
        state.qp += eps
        return state
