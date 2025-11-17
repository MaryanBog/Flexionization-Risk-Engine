"""
Example FRE 2.0 simulation run (5D state version).

- Automatically adds ./src to sys.path
- Uses fre_simulator.engine.run_simulation
- Defines a 5D ExampleState5D with vector deviation Δ = (Δm, ΔL, ΔH, ΔR, ΔC)
- Keeps scalar FXI and scalar delta = ||Δ|| for compatibility with the engine
"""

import sys
import os
import math
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------
# 1. Add ./src to sys.path so that `import fre_simulator` works
# ---------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Now we can safely import the simulator engine
from fre_simulator.engine import run_simulation, SimulationResult  # type: ignore


# ---------------------------------------------------------
# 2. 5D ExampleState compatible with fre_simulator.engine.run_simulation
# ---------------------------------------------------------


@dataclass
class ExampleState5D:
    """
    5D structural state for FRE 2.0 demo.

    Internal structural components:
        m, L, H, R, C      — actual structural configuration
        m_ref, ... ,C_ref  — reference (equilibrium) configuration

    Deviation:
        delta_vec = [Δm, ΔL, ΔH, ΔR, ΔC]
        delta     = ||delta_vec||_2   (scalar, used by engine)

    FXI:
        fxi = F(delta) = 1 + alpha * delta

    Engine expectations:
      - attributes: fxi, delta
      - class attrs: DELTA_MAX, FXI_MIN, FXI_MAX
      - methods:     validate(), compute_delta(), update_from_operator(new_fxi)
    """

    # Actual structural values
    m: float
    L: float
    H: float
    R: float
    C: float

    # Reference (target) values
    m_ref: float
    L_ref: float
    H_ref: float
    R_ref: float
    C_ref: float

    # Derived quantities
    delta: float          # scalar norm ||Δ||
    fxi: float            # FXI indicator

    # Full deviation vector Δ⃗
    delta_vec: List[float] = field(default_factory=list)

    # Structural bounds
    DELTA_MAX: float = 1.0     # max allowed norm of Δ
    FXI_MIN: float = 0.5       # min allowed FXI
    FXI_MAX: float = 1.5       # max allowed FXI

    # Mapping parameter FXI = 1 + alpha * ||Δ||
    ALPHA: float = 0.5

    # -------------------------------------------------
    # Core methods required by the engine
    # -------------------------------------------------

    def _compute_delta_vector(self) -> None:
        """Compute component-wise deviation Δ⃗ = X - X_ref."""
        d_m = self.m - self.m_ref
        d_L = self.L - self.L_ref
        d_H = self.H - self.H_ref
        d_R = self.R - self.R_ref
        d_C = self.C - self.C_ref
        self.delta_vec = [d_m, d_L, d_H, d_R, d_C]

    def compute_delta(self) -> None:
        """
        Recompute Δ⃗ and scalar delta = ||Δ⃗||.

        Engine calls this method each step:
            state.compute_delta()
        """
        self._compute_delta_vector()
        self.delta = math.sqrt(sum(d * d for d in self.delta_vec))

        # Update FXI from delta using simple linear map.
        # FXI > 1  => expanded
        # FXI = 1  => equilibrium
        # FXI < 1  => compressed (в этом демо мы стартуем только > 1).
        self.fxi = 1.0 + self.ALPHA * self.delta

    def validate(self) -> None:
        """
        Simple structural sanity checks.

        In real systems здесь можно зашить реальные лимиты:
        минимальные маржи, капитальные буферы и т.д.
        """
        if self.delta > self.DELTA_MAX * 2:
            raise ValueError(f"Delta norm too large: {self.delta}")

        if not (self.FXI_MIN <= self.fxi <= self.FXI_MAX):
            raise ValueError(f"FXI out of bounds: {self.fxi}")

    def update_from_operator(self, new_fxi: float) -> None:
        """
        Update state from operator result (E in FXI-space).

        Engine calls:
            state.update_from_operator(next_fxi)

        Логика:
          1) принимаем новый FXI,
          2) через обратную связь F^{-1} восстанавливаем новую норму Δ,
          3) масштабируем вектор Δ⃗ вдоль текущего направления,
             чтобы ||Δ⃗|| = delta_new,
          4) получаем новые m, L, H, R, C = ref + Δ⃗_new,
          5) пересчитываем delta и fxi для консистентности.
        """
        self.fxi = new_fxi

        # Если F(delta) = 1 + ALPHA * delta => delta = (fxi - 1) / ALPHA
        delta_new = abs((self.fxi - 1.0) / self.ALPHA)

        # Если текущая delta == 0, то мы уже в точном равновесии:
        # просто оставляем всё на уровне референса.
        if self.delta == 0:
            self.m = self.m_ref
            self.L = self.L_ref
            self.H = self.H_ref
            self.R = self.R_ref
            self.C = self.C_ref
            self.compute_delta()
            return

        # Масштабируем вектор Δ⃗ на новую норму
        scale = delta_new / self.delta
        self._compute_delta_vector()
        d_m, d_L, d_H, d_R, d_C = self.delta_vec

        d_m_new = d_m * scale
        d_L_new = d_L * scale
        d_H_new = d_H * scale
        d_R_new = d_R * scale
        d_C_new = d_C * scale

        # Восстанавливаем структурные компоненты
        self.m = self.m_ref + d_m_new
        self.L = self.L_ref + d_L_new
        self.H = self.H_ref + d_H_new
        self.R = self.R_ref + d_R_new
        self.C = self.C_ref + d_C_new

        # Финальный перерасчёт delta и fxi для консистентности
        self.compute_delta()


# ---------------------------------------------------------
# 3. Simple contractive operator E and trivial scenario
# ---------------------------------------------------------


class SimpleContractiveOperator:
    """
    Very simple contractive operator in FXI-space:

        FXI_{t+1} = 1 + k * (FXI_t - 1),  0 < k < 1

    Это даёт геометрическую сходимость FXI -> 1,
    а через update_from_operator это превращается в сходимость ||Δ⃗|| -> 0.
    """

    def __init__(self, k: float = 0.4) -> None:
        if not (0.0 < k < 1.0):
            raise ValueError("k must be in (0, 1) for contraction")
        self.k = k

    def apply(self, fxi: float) -> float:
        """
        Called by engine as:
            next_fxi = operator.apply(prev_fxi)
        """
        return 1.0 + self.k * (fxi - 1.0)

    def kappa(self, prev_fxi: float, new_fxi: float) -> float:
        """
        Contraction ratio kappa:

            kappa_t = |FXI_{t+1} - 1| / |FXI_t - 1|

        В идеале ~= k.
        """
        prev_dist = abs(prev_fxi - 1.0)
        new_dist = abs(new_fxi - 1.0)
        if prev_dist == 0:
            return 0.0
        return new_dist / prev_dist


class NoShockScenario:
    """
    Trivial scenario: no external shocks, state is unchanged.

    Engine calls:
        state = scenario.apply(state, t)

    Здесь можно будет позже добавить сдвиги по компонентам,
    чтобы моделировать stress-сценарии (ликвидность, маржа и т.д.).
    """

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Пример того, как можно будет добавить стресс:
        # if t == 5:
        #     state.m += 0.2
        #     state.L -= 0.1
        #     state.compute_delta()
        return state


# ---------------------------------------------------------
# 4. Run example simulation
# ---------------------------------------------------------


def main() -> None:
    # Initial 5D structural state:
    #
    # Reference configuration:
    #   m_ref = L_ref = H_ref = R_ref = C_ref = 1.0
    #
    # Actual configuration — немного смещена по всем осям:
    #   m = 1.10 (margin)
    #   L = 0.90 (limits/exposure)
    #   H = 1.05 (hedging/liquidity)
    #   R = 1.20 (risk-parameters)
    #   C = 0.95 (capital buffers)
    #
    # Это даёт ненулевой вектор Δ⃗ и FXI > 1 (расширенное состояние).
    initial_state = ExampleState5D(
        m=1.10,
        L=0.90,
        H=1.05,
        R=1.20,
        C=0.95,
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,   # заполним в compute_delta()
        fxi=1.0,     # заполним в compute_delta()
    )

    # Начальный пересчёт Δ⃗ и FXI
    initial_state.compute_delta()
    initial_state.validate()

    operator = SimpleContractiveOperator(k=0.4)
    scenario = NoShockScenario()

    horizon = 20

    result: SimulationResult = run_simulation(
        initial_state=initial_state,
        operator=operator,
        scenario=scenario,
        horizon=horizon,
        config=None,  # используем дефолтные пороги из двигателя
    )

    # ---- Output ----
    print("FRE 2.0 Example Simulation (5D)")
    print("================================")
    print(f"Horizon: {horizon} steps")
    print(
        f"Initial FXI: {result.fxi_series[0]:.4f}, "
        f"Initial Delta: {result.delta_series[0]:.4f}"
    )
    print()

    header = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header)
    print("-" * len(header))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result.fxi_series,
            result.delta_series,
            result.kappa_series,
            result.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    print()
    print(f"Breach occurred: {result.breach_occurred}")
    if result.breach_occurred:
        print(f"  Step : {result.breach_step}")
        print(f"  Type : {result.breach_type}")


if __name__ == "__main__":
    main()
