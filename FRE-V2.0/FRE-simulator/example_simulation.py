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
    5D structural state for FRE 2.0 demo (with vector operator E).

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

    ВАЖНО: на LEVEL 2 мы вводим настоящий векторный оператор:
        Δ_{t+1} = k_eff * Q * Δ_t,
    где Q — ортогональная матрица (перестановка компонент),
    k_eff — фактический коэффициент сжатия, вычисленный по FXI.
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

    # Mapping parameter FXI = 1 + ALPHA * ||Δ||
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

        # FXI = 1 + alpha * ||Δ||
        self.fxi = 1.0 + self.ALPHA * self.delta

    def validate(self) -> None:
        """
        Simple structural sanity checks.
        """
        if self.delta > self.DELTA_MAX * 2:
            raise ValueError(f"Delta norm too large: {self.delta}")

        if not (self.FXI_MIN <= self.fxi <= self.FXI_MAX):
            raise ValueError(f"FXI out of bounds: {self.fxi}")

    def _apply_Q(self, vec: List[float]) -> List[float]:
        """
        Apply orthogonal matrix Q to Δ⃗.

        Здесь Q — просто перестановка компонент:
            Q * (Δm, ΔL, ΔH, ΔR, ΔC)
              = (ΔL, Δm, ΔH, ΔC, ΔR)

        Такая матрица ортогональна (норма сохраняется),
        но создаёт взаимодействие между осями.
        """
        d_m, d_L, d_H, d_R, d_C = vec
        return [d_L, d_m, d_H, d_C, d_R]

    def update_from_operator(self, new_fxi: float) -> None:
        """
        Update state from operator result (vector E in Δ-space).

        Engine calls:
            state.update_from_operator(next_fxi)

        Логика:
          1) prev_fxi = текущий FXI(t)
          2) k_eff = |(FXI_{t+1} - 1) / (FXI_t - 1)| — фактическая контракция
          3) Δ⃗_t берём из текущего состояния
          4) Δ⃗'_t = Q * Δ⃗_t — поворот / перестановка координат
          5) Δ⃗_{t+1} = k_eff * Δ⃗'_t
          6) обновляем m, L, H, R, C = ref + Δ⃗_{t+1}
          7) пересчитываем delta и fxi => FXI снова согласован с нормой Δ⃗.
        """
        prev_fxi = self.fxi
        self._compute_delta_vector()

        # Если мы уже в точном равновесии (FXI=1, Δ⃗=0),
        # просто остаёмся в точке X*.
        if self.delta == 0 or abs(prev_fxi - 1.0) < 1e-12:
            self.m = self.m_ref
            self.L = self.L_ref
            self.H = self.H_ref
            self.R = self.R_ref
            self.C = self.C_ref
            self.compute_delta()
            return

        # Коэффициент сжатия, реально заданный оператором E в FXI-пространстве
        k_eff = abs((new_fxi - 1.0) / (prev_fxi - 1.0))

        # Применяем матрицу Q (перемешиваем оси)
        rotated = self._apply_Q(self.delta_vec)

        # Вектор после контракции
        new_delta_vec = [k_eff * d for d in rotated]

        # Обновляем структурные компоненты
        self.m = self.m_ref + new_delta_vec[0]
        self.L = self.L_ref + new_delta_vec[1]
        self.H = self.H_ref + new_delta_vec[2]
        self.R = self.R_ref + new_delta_vec[3]
        self.C = self.C_ref + new_delta_vec[4]

        # Финальный перерасчёт delta и fxi для строгой консистентности
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

# ============================================================
#  STRESS TEST 1 — Multi-Component Structural Shock (t = 5)
#
#  This scenario introduces a single strong structural disturbance
#  at step t = 5, affecting three different internal axes of the
#  5-dimensional state:
#
#      • L  (Exposure / Liquidity axis)   →   L -= 0.30
#      • R  (Risk parameters axis)        →   R += 0.30
#      • C  (Capital buffers axis)        →   C -= 0.20
#
#  Interpretation:
#      • Liquidity or exposure suddenly worsens.
#      • Risk parameters spike upward (higher internal stress).
#      • Capital buffers fall (loss / de-leveraging event).
#
#  Model significance:
#      – The stress moves Δ⃗ sharply away from equilibrium,
#        pushing FXI from near-stable → stressed zone.
#      – No discontinuities occur — FRE remains continuous.
#      – The contraction mapping of the FRE operator pulls
#        the system back toward equilibrium after the shock.
#      – Demonstrates stability theorems under real disturbance.
#
#  Summary:
#      This block defines the official “Stress Test 1”
#      for FRE-Simulator V2.0. It serves as a baseline test
#      for system resilience, contraction, and recovery.
# ============================================================

class StressScenario:
    """
    Stress scenario: single multi-component shock at t = 5.

    Engine calls:
        state = scenario.apply(state, t)

    Логика:
      - t < 5  : система эволюционирует нормально
      - t = 5  : резкий стресс по нескольким осям (L, R, C)
      - t > 5  : дальше снова чистая динамика FRE, которая тянет систему к равновесию.

    Это моделирует, например:
      - внезапный отток ликвидности / рост экспозиций (L),
      - усиление риск-параметров / волатильности (R),
      - просадку капитальных буферов (C).
    """

    def __init__(self) -> None:
        self.stress_applied = False

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Однократный стресс на шаге t = 5
        if t == 5 and not self.stress_applied:
            # Текущие значения к этому моменту уже почти около референса (≈1.0),
            # поэтому мы создаём заметное отклонение:
            #
            #   L ↓  на 0.3  (лимиты / ликвидность ухудшаются)
            #   R ↑  на 0.3  (риск-параметры ужесточаются / растут)
            #   C ↓  на 0.2  (капитал проседает)
            #
            # Это даёт векторный стресс:
            #   ΔL ≈ -0.3, ΔR ≈ +0.3, ΔC ≈ -0.2
            # и поднимает FXI в "critical" зону — дальше FRE должен сам стянуть всё обратно.

            state.L -= 0.3
            state.R += 0.3
            state.C -= 0.2

            # Обновляем Δ⃗ и FXI после стресса
            state.compute_delta()
            state.validate()

            self.stress_applied = True

        return state

# NEW: Stress Test 2 — Dual-Shock Scenario (two shocks at t=5 and t=15)
class DualShockScenario:
    """
    Stress Test 2: Dual-Shock Scenario.

    Two shocks:
      - t = 5  : margin + liquidity type stress (m, L, H, C)
      - t = 15 : risk-parameters + capital stress (m, L, H, R, C)

    The scenario keeps FRE continuous and lets the contraction
    dynamics pull the system back to equilibrium after each shock.
    """

    def __init__(self) -> None:
        self.first_shock_applied = False
        self.second_shock_applied = False

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Shock 1 at t = 5: margin + liquidity driven stress
        if t == 5 and not self.first_shock_applied:
            # Δm += 0.25, ΔL += 0.20, ΔH += 0.05, ΔC += -0.05
            state.m += 0.25
            state.L += 0.20
            state.H += 0.05
            state.C -= 0.05

            state.compute_delta()
            state.validate()
            self.first_shock_applied = True

        # Shock 2 at t = 15: risk-parameters + capital stress
        if t == 15 and not self.second_shock_applied:
            # Δm += 0.05, ΔL += 0.10, ΔH += 0.10, ΔR += 0.20, ΔC += -0.15
            state.m += 0.05
            state.L += 0.10
            state.H += 0.10
            state.R += 0.20
            state.C -= 0.15

            state.compute_delta()
            state.validate()
            self.second_shock_applied = True

        return state

# -----------------------------------------------------
# Level 4 — Multi-Axis Asymmetric Stress Scenario
# -----------------------------------------------------

class MultiAxisAsymmetricScenario:
    """
    Level 4: Multi-Axis Asymmetric Stress.

    Three asymmetric shocks across multiple internal axes:
      - t = 7  : L, R, H, C shock (limits + risk + liquidity + capital)
      - t = 18 : m, C, H, L, R shock (margin + capital + liquidity + limits + risk)
      - t = 28 : H, L, R, C shock (liquidity restoration + limits compression)
    """

    def __init__(self) -> None:
        self.shock_1_applied = False
        self.shock_2_applied = False
        self.shock_3_applied = False

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Shock 1 at t = 7: limits and risk expand, liquidity and capital degrade
        if t == 7 and not self.shock_1_applied:
            # ΔL += 0.25, ΔR += 0.15, ΔH += 0.02, ΔC += -0.03
            state.L += 0.25
            state.R += 0.15
            state.H += 0.02
            state.C -= 0.03

            state.compute_delta()
            state.validate()
            self.shock_1_applied = True

        # Shock 2 at t = 18: strong margin and capital stress, with mixed effects
        if t == 18 and not self.shock_2_applied:
            # Δm += 0.30, ΔC += -0.20, ΔH += 0.04, ΔL += -0.05, ΔR += 0.10
            state.m += 0.30
            state.C -= 0.20
            state.H += 0.04
            state.L -= 0.05
            state.R += 0.10

            state.compute_delta()
            state.validate()
            self.shock_2_applied = True

        # Shock 3 at t = 28: liquidity recovers, limits compress, capital stabilizes
        if t == 28 and not self.shock_3_applied:
            # ΔH += -0.20, ΔL += 0.18, ΔR += -0.05, ΔC += 0.10
            state.H -= 0.20
            state.L += 0.18
            state.R -= 0.05
            state.C += 0.10

            state.compute_delta()
            state.validate()
            self.shock_3_applied = True

        return state


# ---------------------------------------------------------
# Run example simulation
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
    scenario = StressScenario()

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

    # ---- NEW: detailed 5D deviation components ----
    print("\nDetailed 5D deviation components (Delta vector):")
    header2 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header2)
    print("-" * len(header2))

    for t, state in enumerate(result.state_series):
        # delta_vec = [Δm, ΔL, ΔH, ΔR, ΔC]
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred: {result.breach_occurred}")
    if result.breach_occurred:
        print(f"  Step : {result.breach_step}")
        print(f"  Type : {result.breach_type}")

    # -----------------------------------------------------
    # Stress Test 2 — Dual-Shock Scenario
    # -----------------------------------------------------
    print("\n\nStress Test 2 — Dual-Shock Scenario (5D)")
    print("=========================================")

    # Initial state for Stress Test 2:
    # near-equilibrium configuration with small deviations:
    #   Δm = 0.03, ΔL = 0.02, ΔH = 0.00, ΔR = 0.00, ΔC = 0.01
    initial_state_2 = ExampleState5D(
        m=1.0 + 0.03,   # m_ref + Δm
        L=1.0 + 0.02,   # L_ref + ΔL
        H=1.0 + 0.00,
        R=1.0 + 0.00,
        C=1.0 + 0.01,
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_2.compute_delta()
    initial_state_2.validate()

    # We reuse the same contractive operator (k = 0.4)
    scenario_2 = DualShockScenario()
    horizon_2 = 30

    result_2: SimulationResult = run_simulation(
        initial_state=initial_state_2,
        operator=operator,
        scenario=scenario_2,
        horizon=horizon_2,
        config=None,
    )

    # ---- Scalar summary table (FXI, Delta, kappa, Zone) for Stress Test 2 ----
    print(f"Horizon: {horizon_2} steps")
    print(
        f"Initial FXI: {result_2.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_2.delta_series[0]:.4f}"
    )
    print()

    header_s2 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_s2)
    print("-" * len(header_s2))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_2.fxi_series,
            result_2.delta_series,
            result_2.kappa_series,
            result_2.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- Detailed 5D deviation components for Stress Test 2 ----
    print("\nDetailed 5D deviation components (Delta vector) — Stress Test 2:")
    header_vec_2 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_2)
    print("-" * len(header_vec_2))

    for t, state in enumerate(result_2.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Stress Test 2): {result_2.breach_occurred}")
    if result_2.breach_occurred:
        print(f"  Step : {result_2.breach_step}")
        print(f"  Type : {result_2.breach_type}")


    # -----------------------------------------------------
    # Level 4 — Multi-Axis Asymmetric Stress (5D)
    # -----------------------------------------------------
    print("\n\nLevel 4 Multi-Axis Asymmetric Stress (5D)")
    print("============================================")
    horizon_4 = 40

    # Initial state for Level 4:
    #   Δm = +0.04, ΔL = -0.03, ΔH = +0.02, ΔR = 0.00, ΔC = -0.01
    initial_state_4 = ExampleState5D(
        m=1.0 + 0.04,   # m_ref + Δm
        L=1.0 - 0.03,   # L_ref + ΔL
        H=1.0 + 0.02,   # H_ref + ΔH
        R=1.0 + 0.00,   # R_ref + ΔR
        C=1.0 - 0.01,   # C_ref + ΔC
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_4.compute_delta()
    initial_state_4.validate()

    scenario_4 = MultiAxisAsymmetricScenario()

    result_4: SimulationResult = run_simulation(
        initial_state=initial_state_4,
        operator=operator,      # same SimpleContractiveOperator(k=0.4)
        scenario=scenario_4,
        horizon=horizon_4,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 4 ----
    print(f"Horizon: {horizon_4} steps")
    print(
        f"Initial FXI: {result_4.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_4.delta_series[0]:.4f}"
    )
    print()

    header_4 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_4)
    print("-" * len(header_4))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_4.fxi_series,
            result_4.delta_series,
            result_4.kappa_series,
            result_4.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a  "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- 5D deviation vector for Level 4 ----
    print("\nDetailed 5D deviation components (Delta vector) Level 4:")
    header_vec_4 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_4)
    print("-" * len(header_vec_4))

    for t, state in enumerate(result_4.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 4): {result_4.breach_occurred}")
    if result_4.breach_occurred:
        print(f"  Step : {result_4.breach_step}")
        print(f"  Type : {result_4.breach_type}")

if __name__ == "__main__":
    main()
