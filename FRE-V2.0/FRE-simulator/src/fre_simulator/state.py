"""
State Module — FRE Simulator V2.0
=================================

This module defines the internal structural state used throughout the
Flexionization Risk Engine (FRE) Version 2.0 simulation framework.

The State object represents the instantaneous structural deviation of the system
and contains:

- FXI:   Equilibrium indicator value at time t
- Delta: Deviation magnitude (scalar or vector, depending on the operator)
- Zone:  Stability zone classification for the current state
- Step:  Discrete time index in the evolution trajectory

The State object is intentionally minimal. It stores only the information
required by the FRE evolution loop and corrective operator E⃗. All dynamics
are implemented in `engine.py`.

This module is fully deterministic and side-effect free.
"""

# state.py
# Structural state representation for FRE Simulator V2.0
# Implements: Δ(t), FXI(t), admissibility checks, and initial state creation.

from dataclasses import dataclass


@dataclass
class State:
    """
    Core structural state of FRE Simulator V2.0.

    Components:
        delta — structural deviation Δ(t)
        fxi   — equilibrium indicator FXI(t)
        qp    — primary structural quantity
        qf    — feedback structural quantity
        q     — structural coefficient
        w, u  — auxiliary operational variables

    All components must satisfy admissibility conditions defined by FRE-2.0.
    """
    delta: float
    fxi: float
    qp: float
    qf: float
    q: float
    w: float
    u: float

    # capacity thresholds (temporary defaults)
    DELTA_MAX = 10.0
    FXI_MIN = 0.1
    FXI_MAX = 5.0

    def validate(self):
        """Validate admissibility conditions for all state components."""
        if abs(self.delta) > self.DELTA_MAX:
            raise ValueError(f"Δ(t)={self.delta} exceeds admissible bound ±{self.DELTA_MAX}")

        if not (self.FXI_MIN <= self.fxi <= self.FXI_MAX):
            raise ValueError(f"FXI(t)={self.fxi} outside admissible range [{self.FXI_MIN}, {self.FXI_MAX}]")

        # qp, qf, q, w, u must be positive (structural quantities)
        for name, value in [("qp", self.qp), ("qf", self.qf), ("q", self.q),
                            ("w", self.w), ("u", self.u)]:
            if value <= 0:
                raise ValueError(f"{name} must be positive, got {value}")

    def compute_delta(self):
        """
        Compute Δ(t).  
        Base formula: Δ = qp/qf - 1  
        (This is a placeholder; full FRE-2.0 deviation mapping is more complex
        and will be implemented later.)
        """
        self.delta = (self.qp / self.qf) - 1.0
        return self.delta

    def compute_fxi(self):
        """
        Compute FXI(t) from Δ(t).  
        Base formula: FXI = 1 + Δ  
        (Placeholder form — the real FXI mapping is non-linear and will be
        implemented later in operators.py)
        """
        self.fxi = 1.0 + self.delta
        return self.fxi

    def update_from_operator(self, new_fxi_value):
        """Update FXI coming from operator E and recompute Δ."""
        self.fxi = new_fxi_value
        # invert Δ = FXI − 1
        self.delta = self.fxi - 1.0
        self.validate()


def initial_state(delta: float, fxi: float, qp: float, qf: float,
                  q: float, w: float, u: float) -> State:
    """
    Helper constructor for initial state S0.
    Validates admissibility immediately.
    """
    state = State(
        delta=delta,
        fxi=fxi,
        qp=qp,
        qf=qf,
        q=q,
        w=w,
        u=u
    )
    state.validate()
    return state
