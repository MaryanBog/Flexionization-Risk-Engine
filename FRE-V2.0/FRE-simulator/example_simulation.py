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
import sys
import os
import math
import random  # <--- ДОБАВЬ ЭТУ СТРОКУ
from dataclasses import dataclass, field
from typing import List
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

# -----------------------------------------------------
# Level 5 - Extreme-Edge Nonlinear Stress Scenario
# -----------------------------------------------------

class ExtremeEdgeScenario:
    """
    Level 5: Extreme-Edge Nonlinear Stress.

    The scenario applies four strong shocks near the edge of the admissible domain:
      - t = 5  : near-critical expansion on already stressed state
      - t = 12 : deep compression (over-conservative reaction)
      - t = 20 : opposite edge expansion (from compressed to expanded)
      - t = 30 : small but sensitive edge-of-domain perturbation
    """

    def __init__(self) -> None:
        self.shock_1_applied = False
        self.shock_2_applied = False
        self.shock_3_applied = False
        self.shock_4_applied = False

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Shock 1 at t = 5: near-critical expansion
        if t == 5 and not self.shock_1_applied:
            # Δm += 0.15, ΔL += 0.12, ΔH += -0.05, ΔR += 0.10, ΔC += -0.10
            state.m += 0.15
            state.L += 0.12
            state.H -= 0.05
            state.R += 0.10
            state.C -= 0.10

            state.compute_delta()
            state.validate()
            self.shock_1_applied = True

        # Shock 2 at t = 12: deep compression / over-conservative reaction
        if t == 12 and not self.shock_2_applied:
            # Δm += -0.40, ΔL += -0.35, ΔH += 0.20, ΔR += -0.25, ΔC += 0.30
            state.m -= 0.40
            state.L -= 0.35
            state.H += 0.20
            state.R -= 0.25
            state.C += 0.30

            state.compute_delta()
            state.validate()
            self.shock_2_applied = True

        # Shock 3 at t = 20: opposite edge expansion from compressed state
        if t == 20 and not self.shock_3_applied:
            # Δm += 0.35, ΔL += 0.40, ΔH += -0.30, ΔR += 0.20, ΔC += -0.25
            state.m += 0.35
            state.L += 0.40
            state.H -= 0.30
            state.R += 0.20
            state.C -= 0.25

            state.compute_delta()
            state.validate()
            self.shock_3_applied = True

        # Shock 4 at t = 30: small but sensitive edge-of-domain perturbation
        if t == 30 and not self.shock_4_applied:
            # Δm += 0.05, ΔL += -0.07, ΔH += 0.06, ΔR += -0.04, ΔC += 0.05
            state.m += 0.05
            state.L -= 0.07
            state.H += 0.06
            state.R -= 0.04
            state.C += 0.05

            state.compute_delta()
            state.validate()
            self.shock_4_applied = True

        return state

# -----------------------------------------------------
# Level 6 - Chaotic Orbit Suppression Stress Scenario
# -----------------------------------------------------

class ChaoticOrbitScenario:
    """
    Level 6: Chaotic Orbit Suppression Stress.

    This scenario applies a sequence of small and medium shocks
    that mimic chaotic external excitation:

      - Phase A (t = 3..15): high-frequency micro-shocks every 2 steps
      - Phase B (t = 18, 19): quasi-resonance double shock
      - Phase C (t = 25..35): low-frequency swaying every 3 steps
      - Phase D (t = 40, 45): final asymmetric chaotic kicks

    The FRE dynamics should contract these pseudo-chaotic orbits
    back towards equilibrium without divergence or persistent oscillations.
    """

    def __init__(self) -> None:
        self.applied_times: set[int] = set()

    def _apply_if_needed(
        self,
        state: ExampleState5D,
        t: int,
        dm: float,
        dL: float,
        dH: float,
        dR: float,
        dC: float,
    ) -> None:
        if t in self.applied_times:
            return
        self.applied_times.add(t)

        state.m += dm
        state.L += dL
        state.H += dH
        state.R += dR
        state.C += dC

        state.compute_delta()
        state.validate()

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # ------------------------------
        # Phase A: high-frequency micro-shocks (t = 3,5,7,9,11,13,15)
        # ------------------------------
        if t == 3:
            # small shift, slightly increasing asymmetry
            self._apply_if_needed(state, t, dm=+0.02, dL=-0.01, dH=+0.01, dR=0.00, dC=-0.01)

        if t == 5:
            # reverse direction on some axes
            self._apply_if_needed(state, t, dm=-0.03, dL=+0.02, dH=0.00, dR=+0.01, dC=+0.01)

        if t == 7:
            # another small perturbation with mixed signs
            self._apply_if_needed(state, t, dm=+0.01, dL=+0.01, dH=-0.02, dR=-0.01, dC=+0.01)

        if t == 9:
            self._apply_if_needed(state, t, dm=-0.02, dL=-0.01, dH=+0.01, dR=+0.02, dC=-0.01)

        if t == 11:
            self._apply_if_needed(state, t, dm=+0.02, dL=-0.02, dH=+0.01, dR=-0.01, dC=+0.02)

        if t == 13:
            self._apply_if_needed(state, t, dm=-0.01, dL=+0.01, dH=-0.01, dR=+0.01, dC=-0.02)

        if t == 15:
            self._apply_if_needed(state, t, dm=+0.01, dL=+0.02, dH=0.00, dR=-0.02, dC=+0.01)

        # ------------------------------
        # Phase B: quasi-resonance double shock (t = 18, 19)
        # ------------------------------
        if t == 18:
            # strong push in one direction
            self._apply_if_needed(state, t, dm=+0.08, dL=+0.06, dH=-0.05, dR=+0.04, dC=-0.06)

        if t == 19:
            # almost mirrored correction in the opposite direction
            self._apply_if_needed(state, t, dm=-0.06, dL=-0.05, dH=+0.04, dR=-0.03, dC=+0.05)

        # ------------------------------
        # Phase C: low-frequency swaying (t = 25, 28, 31, 34)
        # ------------------------------
        if t == 25:
            self._apply_if_needed(state, t, dm=+0.05, dL=-0.03, dH=+0.02, dR=-0.02, dC=+0.03)

        if t == 28:
            self._apply_if_needed(state, t, dm=-0.04, dL=+0.04, dH=-0.03, dR=+0.03, dC=-0.02)

        if t == 31:
            self._apply_if_needed(state, t, dm=+0.03, dL=-0.02, dH=+0.02, dR=-0.02, dC=+0.02)

        if t == 34:
            self._apply_if_needed(state, t, dm=-0.02, dL=+0.03, dH=-0.02, dR=+0.02, dC=-0.02)

        # ------------------------------
        # Phase D: final chaotic kicks (t = 40, 45)
        # ------------------------------
        if t == 40:
            self._apply_if_needed(state, t, dm=+0.07, dL=+0.02, dH=-0.04, dR=+0.03, dC=-0.05)

        if t == 45:
            self._apply_if_needed(state, t, dm=-0.05, dL=-0.03, dH=+0.03, dR=-0.02, dC=+0.04)

        return state

# -----------------------------------------------------
# Level 7 - Multi-Frequency Resonance Stress Scenario
# -----------------------------------------------------

class ResonanceScenario:
    """
    Level 7: Multi-Frequency Resonance Stress.

    Three overlapping frequency bands:
      - Low-frequency (LF):   period ~20, medium shocks (t = 10, 30, 50, 70, 90, 110)
      - Mid-frequency (MF):   period ~8,  small/medium shocks (t = 8,16,24,...)
      - High-frequency (HF):  period ~3,  micro-shocks (t = 3,6,9,...)

    The goal is to test whether FRE remains resonance-resistant
    under multi-frequency excitation and does not lock into
    persistent oscillations or diverging orbits.
    """

    def __init__(self) -> None:
        pass

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        dm = 0.0
        dL = 0.0
        dH = 0.0
        dR = 0.0
        dC = 0.0

        # ------------------------------
        # Low-frequency wave (LF): period ~20
        # t = 10, 30, 50, 70, 90, 110
        # amplitude ~0.05 - 0.08 with alternating signs
        # ------------------------------
        if t in (10, 30, 50, 70, 90, 110):
            lf_index = (t - 10) // 20  # 0..5

            lf_patterns = [
                # dm,   dL,    dH,    dR,    dC
                ( +0.05, -0.04, +0.03, -0.02, +0.05),  # t=10
                ( -0.06, +0.05, -0.04, +0.03, -0.06),  # t=30
                ( +0.07, +0.02, -0.05, -0.03, +0.04),  # t=50
                ( -0.05, -0.04, +0.04, +0.02, -0.05),  # t=70
                ( +0.06, -0.03, +0.03, -0.04, +0.06),  # t=90
                ( -0.07, +0.04, -0.03, +0.03, -0.04),  # t=110
            ]

            lf_dm, lf_dL, lf_dH, lf_dR, lf_dC = lf_patterns[lf_index]
            dm += lf_dm
            dL += lf_dL
            dH += lf_dH
            dR += lf_dR
            dC += lf_dC

        # ------------------------------
        # Mid-frequency wave (MF): period ~8
        # t = 8,16,24,32,40,48,56,64,72,80,88,96,104,112
        # amplitude ~0.01 - 0.03
        # ------------------------------
        if 8 <= t <= 112 and (t - 8) % 8 == 0:
            mf_index = (t - 8) // 8  # 0..

            mf_patterns = [
                (+0.02, -0.01, +0.01, +0.00, -0.02),  # 8
                (-0.03, +0.02, -0.01, -0.01, +0.02),  # 16
                (+0.01, +0.01, -0.02, +0.02, -0.01),  # 24
                (-0.02, -0.01, +0.01, +0.02, +0.00),  # 32
                (+0.03, -0.02, +0.00, -0.02, +0.02),  # 40
                (-0.02, +0.01, -0.02, +0.01, -0.02),  # 48
                (+0.01, +0.02, -0.01, -0.02, +0.01),  # 56
                (-0.03, -0.01, +0.02, +0.01, -0.01),  # 64
                (+0.02, -0.01, +0.01, -0.01, +0.02),  # 72
                (-0.01, +0.02, -0.02, +0.02, -0.02),  # 80
                (+0.02, +0.01, -0.01, -0.01, +0.01),  # 88
                (-0.02, -0.02, +0.02, +0.01, -0.01),  # 96
                (+0.03, +0.00, -0.02, -0.02, +0.02),  # 104
                (-0.02, +0.01, +0.00, +0.02, -0.02),  # 112
            ]

            mf_index = min(mf_index, len(mf_patterns) - 1)
            mf_dm, mf_dL, mf_dH, mf_dR, mf_dC = mf_patterns[mf_index]
            dm += mf_dm
            dL += mf_dL
            dH += mf_dH
            dR += mf_dR
            dC += mf_dC

        # ------------------------------
        # High-frequency wave (HF): period ~3
        # t = 3,6,9,...,117
        # amplitude ~0.003 - 0.01
        # ------------------------------
        if 3 <= t <= 117 and (t - 3) % 3 == 0:
            hf_index = (t - 3) // 3

            hf_patterns = [
                (+0.005, -0.003, +0.002, -0.002, +0.004),  # base
                (-0.004, +0.004, -0.003, +0.002, -0.003),
                (+0.006, +0.002, -0.002, +0.003, -0.004),
                (-0.005, -0.002, +0.002, -0.003, +0.003),
            ]
            # cycle through patterns
            hf_dm, hf_dL, hf_dH, hf_dR, hf_dC = hf_patterns[hf_index % len(hf_patterns)]
            dm += hf_dm
            dL += hf_dL
            dH += hf_dH
            dR += hf_dR
            dC += hf_dC

        # ------------------------------
        # Apply combined shock if any
        # ------------------------------
        if dm != 0.0 or dL != 0.0 or dH != 0.0 or dR != 0.0 or dC != 0.0:
            state.m += dm
            state.L += dL
            state.H += dH
            state.R += dR
            state.C += dC

            state.compute_delta()
            state.validate()

        return state

# -----------------------------------------------------
# Level 8 - Domain Shift Stress Scenario (5D)
# -----------------------------------------------------

class DomainShiftScenario:
    """
    Level 8: Domain Shift Stress (5D).

    Суть:
      - На шагах t = 15, 30, 45, 60 система НЕ получает прямой шок по X,
        а внезапно меняет целевой reference-вектор R⃗_ref.
      - Это имитирует смену домена / регуляторных требований / риск-политики:
          • новые целевые margin / limits / hedging / risk / capital,
          • фактическое X остаётся тем же,
          • но Δ⃗ = X - R⃗_ref резко меняется.
      - FRE должен:
          • пережить скачок в Δ⃗ без разрыва траектории,
          • перестроить contraction mapping по новому FXI,
          • продолжить устойчивую сходимость к новому равновесию.
    """

    def __init__(self) -> None:
        # Моменты смены reference-вектора
        self.shift_times = (15, 30, 45, 60)

        # Новый целевой reference для каждого шага (асимметричные смещения в 5D)
        # Формат: (m_ref, L_ref, H_ref, R_ref, C_ref)
        self.reference_patterns = {
            15: (1.02, 0.98, 1.03, 1.01, 0.97),
            30: (0.97, 1.05, 0.96, 1.02, 1.00),
            45: (1.04, 0.96, 1.01, 1.03, 0.95),
            60: (1.00, 1.00, 1.00, 1.00, 1.00),  # возврат к симметричному референсу
        }

        # Чтобы не применять одно и то же смещение дважды
        self.applied_shifts: set[int] = set()

    def _apply_reference_shift(
        self,
        state: ExampleState5D,
        new_m_ref: float,
        new_L_ref: float,
        new_H_ref: float,
        new_R_ref: float,
        new_C_ref: float,
    ) -> None:
        """
        Вспомогательная функция:

          1) меняем reference-вектор R⃗_ref,
          2) пересчитываем Δ⃗ = X - R⃗_ref и FXI,
          3) валидируем состояние.

        Фактическое X не меняется — меняются только цели.
        """
        state.m_ref = new_m_ref
        state.L_ref = new_L_ref
        state.H_ref = new_H_ref
        state.R_ref = new_R_ref
        state.C_ref = new_C_ref

        # Новый Δ⃗ и FXI относительно обновлённого референса
        state.compute_delta()
        state.validate()

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # Если текущий шаг — момент смены reference-вектора
        if t in self.shift_times and t not in self.applied_shifts:
            new_refs = self.reference_patterns.get(t)
            if new_refs is not None:
                self._apply_reference_shift(
                    state,
                    new_m_ref=new_refs[0],
                    new_L_ref=new_refs[1],
                    new_H_ref=new_refs[2],
                    new_R_ref=new_refs[3],
                    new_C_ref=new_refs[4],
                )
                self.applied_shifts.add(t)

        return state

# -----------------------------------------------------
# Level 9 - Slow Domain Drift Scenario (5D)
# -----------------------------------------------------

class DomainDriftScenario:
    """
    Level 9: Slow Domain Drift + Moving Reference (5D).

    Идея:
      - Целевой reference-вектор R⃗_ref(t) медленно дрейфует во времени
        по гладкой 5D-траектории (низкочастотная орбита).
      - Фактическое состояние X почти не получает резких шоков:
        главный стресс в том, что "цель постоянно уезжает".
      - В отдельные моменты (t = 20, 40, 60) добавляется небольшой
        структурный "twist", который имитирует вращение осей / домена
        под дрейфующим равновесием.
      - FRE должен:
          • отслеживать движущееся равновесие,
          • сохранять FXI в допустимых зонах,
          • не переходить в устойчивые орбиты или раскачку.
    """

    def __init__(self) -> None:
        # Амплитуды дрейфа по каждой оси
        self.drift_amplitude = {
            "m": 0.03,
            "L": 0.025,
            "H": 0.02,
            "R": 0.03,
            "C": 0.025,
        }
        # Период полной "орбиты" reference-вектора
        self.period = 60.0

        # Моменты небольших структурных "твистов"
        self.twist_times = (20, 40, 60)
        self.twist_scale = 0.05  # интенсивность поворота

    def _update_references(self, state: ExampleState5D, t: int) -> None:
        """
        Обновляем R⃗_ref(t) по плавной синусоидальной траектории в 5D.
        """
        phi = 2.0 * math.pi * (t / self.period)

        # Разные фазовые сдвиги по компонентам => "вращающийся" reference-домен
        m_ref = 1.0 + self.drift_amplitude["m"] * math.sin(phi)
        L_ref = 1.0 + self.drift_amplitude["L"] * math.sin(phi + math.pi / 3.0)
        H_ref = 1.0 + self.drift_amplitude["H"] * math.sin(phi + 2.0 * math.pi / 3.0)
        R_ref = 1.0 + self.drift_amplitude["R"] * math.sin(phi + math.pi)
        C_ref = 1.0 + self.drift_amplitude["C"] * math.sin(phi + 4.0 * math.pi / 3.0)

        state.m_ref = m_ref
        state.L_ref = L_ref
        state.H_ref = H_ref
        state.R_ref = R_ref
        state.C_ref = C_ref

        # Новый Δ⃗ и FXI относительно дрейфующего равновесия
        state.compute_delta()
        state.validate()

    def _apply_twist(self, state: ExampleState5D) -> None:
        """
        Малый "поворот" структуры: слегка перемешиваем оси
        на основе текущего отклонения Δ⃗.

        Это приближённо имитирует медленно вращающуюся Q-матрицу:
          - часть Δ_m уходит в L,
          - часть Δ_L в H,
          - часть Δ_H в R,
          - часть Δ_R в C,
          - часть Δ_C обратно в m.
        """
        d_m, d_L, d_H, d_R, d_C = state.delta_vec

        state.m += self.twist_scale * (d_L - d_m)
        state.L += self.twist_scale * (d_H - d_L)
        state.H += self.twist_scale * (d_R - d_H)
        state.R += self.twist_scale * (d_C - d_R)
        state.C += self.twist_scale * (d_m - d_C)

        state.compute_delta()
        state.validate()

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        # 1) На КАЖДОМ шаге — плавный дрейф reference-домена
        self._update_references(state, t)

        # 2) В отдельные моменты — небольшой структурный twist
        if t in self.twist_times:
            self._apply_twist(state)

        return state

# -----------------------------------------------------
# Level 10 - Stochastic Drift + Gaussian Shocks (5D)
# -----------------------------------------------------

class StochasticDriftScenario:
    """
    Level 10: Stochastic Drift + Gaussian Shocks (5D).

    Идея:
      - Reference-домен R⃗_ref(t) дрейфует по гладкой орбите, как в Level 9,
        но поверх этого добавляется стохастический шум (Gaussian).
      - Фактический X получает:
          • частые мелкие "micro-shocks" (гауссов шум по осям),
          • редкие "macro-shocks" (более сильные, но всё ещё в допустимой зоне),
          • периодические лёгкие "twist"-повороты структуры (как медленное
            вращение Q-матрицы).
      - FRE должен:
          • не развалиться под стохастикой,
          • удерживать FXI в узкой полосе вокруг 1,
          • не входить в резонанс / орбитальные циклы,
          • не допустить breach по внутренним ограничениям.
    """

    def __init__(self) -> None:
        # Гладкий дрейф reference-домена (как Level 9, но чуть мягче)
        self.drift_amplitude = {
            "m": 0.02,
            "L": 0.018,
            "H": 0.015,
            "R": 0.02,
            "C": 0.018,
        }
        self.period = 80.0  # медленный обход орбиты

        # Стохастика в reference (domain noise)
        self.ref_noise_sigma = {
            "m": 0.004,
            "L": 0.004,
            "H": 0.003,
            "R": 0.004,
            "C": 0.003,
        }

        # Micro-shocks по X (мелкий структурный шум каждый шаг с вероятностью p)
        self.micro_shock_sigma = {
            "m": 0.004,
            "L": 0.004,
            "H": 0.003,
            "R": 0.004,
            "C": 0.003,
        }
        self.micro_shock_prob = 0.25  # 25% шагов получают мелкий шок

        # Редкие macro-shocks (чуть сильнее, но всё ещё внутри допустимой области)
        self.macro_shock_times = (30, 60, 90)
        self.macro_shock_sigma = {
            "m": 0.015,
            "L": 0.015,
            "H": 0.010,
            "R": 0.015,
            "C": 0.010,
        }

        # Лёгкий twist структуры (вращение отклонений между осями)
        self.twist_scale = 0.02   # чуть мягче, чем в Level 9
        self.twist_period = 25    # каждые 25 шагов лёгкий поворот

    # ---------------------------
    # Вспомогательные методы
    # ---------------------------

    def _smooth_reference(self, t: int) -> tuple[float, float, float, float, float]:
        """
        Гладкий базовый дрейф reference-вектора по синусоидальной орбите.
        """
        phi = 2.0 * math.pi * (t / self.period)

        m_ref = 1.0 + self.drift_amplitude["m"] * math.sin(phi)
        L_ref = 1.0 + self.drift_amplitude["L"] * math.sin(phi + math.pi / 3.0)
        H_ref = 1.0 + self.drift_amplitude["H"] * math.sin(phi + 2.0 * math.pi / 3.0)
        R_ref = 1.0 + self.drift_amplitude["R"] * math.sin(phi + math.pi)
        C_ref = 1.0 + self.drift_amplitude["C"] * math.sin(phi + 4.0 * math.pi / 3.0)

        return m_ref, L_ref, H_ref, R_ref, C_ref

    def _apply_reference_update(self, state: ExampleState5D, t: int) -> None:
        """
        Обновляем reference-вектор:
          • гладкий дрейф,
          • плюс стохастический Gaussian-noise.
        """
        base_m, base_L, base_H, base_R, base_C = self._smooth_reference(t)

        # Gaussian шум поверх гладкой орбиты
        state.m_ref = base_m + random.gauss(0.0, self.ref_noise_sigma["m"])
        state.L_ref = base_L + random.gauss(0.0, self.ref_noise_sigma["L"])
        state.H_ref = base_H + random.gauss(0.0, self.ref_noise_sigma["H"])
        state.R_ref = base_R + random.gauss(0.0, self.ref_noise_sigma["R"])
        state.C_ref = base_C + random.gauss(0.0, self.ref_noise_sigma["C"])

        state.compute_delta()
        state.validate()

    def _apply_micro_shock(self, state: ExampleState5D) -> None:
        """
        Мелкий шок по X (структура), Gaussian по каждой оси.
        """
        state.m += random.gauss(0.0, self.micro_shock_sigma["m"])
        state.L += random.gauss(0.0, self.micro_shock_sigma["L"])
        state.H += random.gauss(0.0, self.micro_shock_sigma["H"])
        state.R += random.gauss(0.0, self.micro_shock_sigma["R"])
        state.C += random.gauss(0.0, self.micro_shock_sigma["C"])

        state.compute_delta()
        state.validate()

    def _apply_macro_shock(self, state: ExampleState5D) -> None:
        """
        Редкий, более сильный stochastic-шок по X.
        """
        state.m += random.gauss(0.0, self.macro_shock_sigma["m"])
        state.L += random.gauss(0.0, self.macro_shock_sigma["L"])
        state.H += random.gauss(0.0, self.macro_shock_sigma["H"])
        state.R += random.gauss(0.0, self.macro_shock_sigma["R"])
        state.C += random.gauss(0.0, self.macro_shock_sigma["C"])

        state.compute_delta()
        state.validate()

    def _apply_twist(self, state: ExampleState5D) -> None:
        """
        Лёгкий структурный twist: перемешивание компонет Δ⃗.
        """
        # гарантируем актуальный Δ⃗
        state.compute_delta()
        d_m, d_L, d_H, d_R, d_C = state.delta_vec

        state.m += self.twist_scale * (d_L - d_m)
        state.L += self.twist_scale * (d_H - d_L)
        state.H += self.twist_scale * (d_R - d_H)
        state.R += self.twist_scale * (d_C - d_R)
        state.C += self.twist_scale * (d_m - d_C)

        state.compute_delta()
        state.validate()

    # ---------------------------
    # Основной интерфейс сценария
    # ---------------------------

    def apply(self, state: ExampleState5D, t: int) -> ExampleState5D:
        """
        Engine вызывает:
            state = scenario.apply(state, t)

        Порядок:
          1) Дрейф + шум reference-домена.
          2) С вероятностью p — micro-shock по X.
          3) В редкие времена — macro-shock по X.
          4) Каждые twist_period шагов — лёгкий twist структуры.

        Важно:
          - Сценарий не ломает непрерывность FXI,
          - Всё остаётся в рамках FRE-констракции с contraction-оператором.
        """
        # 1) Всегда обновляем reference-домен (drift + Gaussian noise)
        self._apply_reference_update(state, t)

        # 2) Micro-shock по X с вероятностью p
        if random.random() < self.micro_shock_prob:
            self._apply_micro_shock(state)

        # 3) Редкие macro-shocks в заранее заданные моменты
        if t in self.macro_shock_times:
            self._apply_macro_shock(state)

        # 4) Периодический twist структуры
        if t > 0 and (t % self.twist_period == 0):
            self._apply_twist(state)

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

    # -----------------------------------------------------
    # Level 5 - Extreme-Edge Nonlinear Stress (5D)
    # -----------------------------------------------------
    print("\n\nLevel 5 - Extreme-Edge Nonlinear Stress (5D)")
    print("==============================================")
    horizon_5 = 50

    # Initial state for Level 5:
    #   Δm = +0.20, ΔL = +0.18, ΔH = -0.15, ΔR = +0.10, ΔC = -0.18
    initial_state_5 = ExampleState5D(
        m=1.0 + 0.20,   # m_ref + Δm
        L=1.0 + 0.18,   # L_ref + ΔL
        H=1.0 - 0.15,   # H_ref + ΔH
        R=1.0 + 0.10,   # R_ref + ΔR
        C=1.0 - 0.18,   # C_ref + ΔC
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_5.compute_delta()
    initial_state_5.validate()

    scenario_5 = ExtremeEdgeScenario()

    result_5: SimulationResult = run_simulation(
        initial_state=initial_state_5,
        operator=operator,      # same SimpleContractiveOperator(k=0.4)
        scenario=scenario_5,
        horizon=horizon_5,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 5 ----
    print(f"Horizon: {horizon_5} steps")
    print(
        f"Initial FXI: {result_5.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_5.delta_series[0]:.4f}"
    )
    print()

    header_5 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_5)
    print("-" * len(header_5))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_5.fxi_series,
            result_5.delta_series,
            result_5.kappa_series,
            result_5.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a  "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- 5D deviation vector for Level 5 ----
    print("\nDetailed 5D deviation components (Delta vector) Level 5:")
    header_vec_5 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_5)
    print("-" * len(header_vec_5))

    for t, state in enumerate(result_5.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 5): {result_5.breach_occurred}")
    if result_5.breach_occurred:
        print(f"  Step : {result_5.breach_step}")
        print(f"  Type : {result_5.breach_type}")

    # -----------------------------------------------------
    # Level 6 - Chaotic Orbit Suppression Stress (5D)
    # -----------------------------------------------------
    print("\n\nLevel 6 - Chaotic Orbit Suppression Stress (5D)")
    print("================================================")
    horizon_6 = 60

    # Initial state for Level 6:
    #   Δm = +0.06, ΔL = -0.04, ΔH = +0.03, ΔR = -0.02, ΔC = +0.05
    initial_state_6 = ExampleState5D(
        m=1.0 + 0.06,   # m_ref + Δm
        L=1.0 - 0.04,   # L_ref + ΔL
        H=1.0 + 0.03,   # H_ref + ΔH
        R=1.0 - 0.02,   # R_ref + ΔR
        C=1.0 + 0.05,   # C_ref + ΔC
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_6.compute_delta()
    initial_state_6.validate()

    scenario_6 = ChaoticOrbitScenario()

    result_6: SimulationResult = run_simulation(
        initial_state=initial_state_6,
        operator=operator,      # same SimpleContractiveOperator(k=0.4)
        scenario=scenario_6,
        horizon=horizon_6,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 6 ----
    print(f"Horizon: {horizon_6} steps")
    print(
        f"Initial FXI: {result_6.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_6.delta_series[0]:.4f}"
    )
    print()

    header_6 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_6)
    print("-" * len(header_6))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_6.fxi_series,
            result_6.delta_series,
            result_6.kappa_series,
            result_6.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a  "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- 5D deviation vector for Level 6 ----
    print("\nDetailed 5D deviation components (Delta vector) Level 6:")
    header_vec_6 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_6)
    print("-" * len(header_vec_6))

    for t, state in enumerate(result_6.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 6): {result_6.breach_occurred}")
    if result_6.breach_occurred:
        print(f"  Step : {result_6.breach_step}")
        print(f"  Type : {result_6.breach_type}")

    # -----------------------------------------------------
    # Level 7 - Multi-Frequency Resonance Stress (5D)
    # -----------------------------------------------------
    print("\n\nLevel 7 - Multi-Frequency Resonance Stress (5D)")
    print("================================================")
    horizon_7 = 120

    # Initial state for Level 7:
    #   Δm = +0.03, ΔL = +0.02, ΔH = -0.02, ΔR = +0.01, ΔC = -0.03
    initial_state_7 = ExampleState5D(
        m=1.0 + 0.03,   # m_ref + Δm
        L=1.0 + 0.02,   # L_ref + ΔL
        H=1.0 - 0.02,   # H_ref + ΔH
        R=1.0 + 0.01,   # R_ref + ΔR
        C=1.0 - 0.03,   # C_ref + ΔC
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_7.compute_delta()
    initial_state_7.validate()

    scenario_7 = ResonanceScenario()

    result_7: SimulationResult = run_simulation(
        initial_state=initial_state_7,
        operator=operator,      # same SimpleContractiveOperator(k=0.4)
        scenario=scenario_7,
        horizon=horizon_7,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 7 ----
    print(f"Horizon: {horizon_7} steps")
    print(
        f"Initial FXI: {result_7.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_7.delta_series[0]:.4f}"
    )
    print()

    header_7 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_7)
    print("-" * len(header_7))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_7.fxi_series,
            result_7.delta_series,
            result_7.kappa_series,
            result_7.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a   "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- 5D deviation vector for Level 7 ----
    print("\nDetailed 5D deviation components (Delta vector) Level 7:")
    header_vec_7 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_7)
    print("-" * len(header_vec_7))

    for t, state in enumerate(result_7.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 7): {result_7.breach_occurred}")
    if result_7.breach_occurred:
        print(f"  Step : {result_7.breach_step}")
        print(f"  Type : {result_7.breach_type}")

    # -----------------------------------------------------
    # Level 8 — Domain Shift Stress (5D)
    # -----------------------------------------------------
    print("\n\nLevel 8 — Domain Shift Stress (5D)")
    print("====================================")
    horizon_8 = 80

    # Initial state for Level 8:
    #   небольшие асимметрии + нормальная зона
    initial_state_8 = ExampleState5D(
        m=1.0 + 0.04,
        L=1.0 - 0.02,
        H=1.0 + 0.03,
        R=1.0 - 0.01,
        C=1.0 + 0.02,
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_8.compute_delta()
    initial_state_8.validate()

    scenario_8 = DomainShiftScenario()

    result_8: SimulationResult = run_simulation(
        initial_state=initial_state_8,
        operator=operator,     # тот же SimpleContractiveOperator(k=0.4)
        scenario=scenario_8,
        horizon=horizon_8,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 8 ----
    print(f"Horizon: {horizon_8} steps")
    print(
        f"Initial FXI: {result_8.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_8.delta_series[0]:.4f}"
    )
    print()

    header_8 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_8)
    print("-" * len(header_8))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_8.fxi_series,
            result_8.delta_series,
            result_8.kappa_series,
            result_8.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a   "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- Detailed 5D deviation components for Level 8 ----
    print("\nDetailed 5D deviation components (Delta vector) — Level 8:")
    header_vec_8 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_8)
    print("-" * len(header_vec_8))

    for t, state in enumerate(result_8.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 8): {result_8.breach_occurred}")
    if result_8.breach_occurred:
        print(f"  Step : {result_8.breach_step}")
        print(f"  Type : {result_8.breach_type}")

    # -----------------------------------------------------
    # Level 9 — Slow Domain Drift + Moving Reference (5D)
    # -----------------------------------------------------
    print("\n\nLevel 9 — Slow Domain Drift (5D)")
    print("===================================")
    horizon_9 = 120

    # Initial state for Level 9:
    #   лёгкая асимметрия, всё в допустимой зоне
    initial_state_9 = ExampleState5D(
        m=1.0 + 0.05,
        L=1.0 - 0.03,
        H=1.0 + 0.04,
        R=1.0 - 0.02,
        C=1.0 + 0.03,
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_9.compute_delta()
    initial_state_9.validate()

    scenario_9 = DomainDriftScenario()

    result_9: SimulationResult = run_simulation(
        initial_state=initial_state_9,
        operator=operator,     # SimpleContractiveOperator(k=0.4)
        scenario=scenario_9,
        horizon=horizon_9,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 9 ----
    print(f"Horizon: {horizon_9} steps")
    print(
        f"Initial FXI: {result_9.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_9.delta_series[0]:.4f}"
    )
    print()

    header_9 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_9)
    print("-" * len(header_9))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_9.fxi_series,
            result_9.delta_series,
            result_9.kappa_series,
            result_9.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a   "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- Detailed 5D deviation vector for Level 9 ----
    print("\nDetailed 5D deviation components (Delta vector) — Level 9:")
    header_vec_9 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_9)
    print("-" * len(header_vec_9))

    for t, state in enumerate(result_9.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 9): {result_9.breach_occurred}")
    if result_9.breach_occurred:
        print(f"  Step : {result_9.breach_step}")
        print(f"  Type : {result_9.breach_type}")

    # -----------------------------------------------------
    # Level 10 — Stochastic Drift + Gaussian Chaos (5D)
    # -----------------------------------------------------
    print("\n\nLevel 10 — Stochastic Drift + Gaussian Chaos (5D)")
    print("====================================================")
    horizon_10 = 150

    # Initial state for Level 10:
    #   Лёгкая асимметрия, всё в допустимой зоне.
    initial_state_10 = ExampleState5D(
        m=1.0 + 0.04,
        L=1.0 - 0.03,
        H=1.0 + 0.02,
        R=1.0 - 0.01,
        C=1.0 + 0.03,
        m_ref=1.0,
        L_ref=1.0,
        H_ref=1.0,
        R_ref=1.0,
        C_ref=1.0,
        delta=0.0,
        fxi=1.0,
    )

    initial_state_10.compute_delta()
    initial_state_10.validate()

    scenario_10 = StochasticDriftScenario()

    result_10: SimulationResult = run_simulation(
        initial_state=initial_state_10,
        operator=operator,      # SimpleContractiveOperator(k=0.4)
        scenario=scenario_10,
        horizon=horizon_10,
        config=None,
    )

    # ---- Scalar FXI/Delta summary for Level 10 ----
    print(f"Horizon: {horizon_10} steps")
    print(
        f"Initial FXI: {result_10.fxi_series[0]:.4f}, "
        f"Initial Delta: {result_10.delta_series[0]:.4f}"
    )
    print()

    header_10 = f"{'t':>3} | {'FXI':>8} | {'Delta':>8} | {'kappa':>8} | Zone"
    print(header_10)
    print("-" * len(header_10))

    for t, (fxi, delta, kappa, zone) in enumerate(
        zip(
            result_10.fxi_series,
            result_10.delta_series,
            result_10.kappa_series,
            result_10.stability_zones,
        )
    ):
        kappa_str = f"{kappa:.4f}" if kappa is not None else "   n/a   "
        print(f"{t:3d} | {fxi:8.4f} | {delta:8.4f} | {kappa_str:>8} | {zone}")

    # ---- Detailed 5D deviation vector for Level 10 ----
    print("\nDetailed 5D deviation components (Delta vector) — Level 10:")
    header_vec_10 = (
        f"{'t':>3} | {'d_m':>8} | {'d_L':>8} | "
        f"{'d_H':>8} | {'d_R':>8} | {'d_C':>8} | {'norm':>8}"
    )
    print(header_vec_10)
    print("-" * len(header_vec_10))

    for t, state in enumerate(result_10.state_series):
        d_m, d_L, d_H, d_R, d_C = state.delta_vec
        norm_val = (d_m**2 + d_L**2 + d_H**2 + d_R**2 + d_C**2) ** 0.5
        print(
            f"{t:3d} | {d_m:8.4f} | {d_L:8.4f} | "
            f"{d_H:8.4f} | {d_R:8.4f} | {d_C:8.4f} | {norm_val:8.4f}"
        )

    print()
    print(f"Breach occurred (Level 10): {result_10.breach_occurred}")
    if result_10.breach_occurred:
        print(f"  Step : {result_10.breach_step}")
        print(f"  Type : {result_10.breach_type}")

if __name__ == "__main__":
    main()
