"""
FRE Demo #3 — Collapse Boundary (κ → 0)

This demo illustrates:
- how contractivity κ evolves,
- how the system approaches the viability boundary κ → 0,
- how Δ and FXI behave near the boundary.

Conceptual demonstration, independent of the full simulator.
"""

import math

# initial structural state
delta = 0.30        # structural deviation
kappa = 0.80        # contractivity (viability if κ >= 0)
alpha = 0.5         # FXI sensitivity
k_base = 0.40       # base contraction
k_degrade = 0.03    # degradation factor for κ

def E(d, k):
    """Contractive operator with adjustable strength k."""
    return k * d

print("FRE Demo #3 — Collapse Boundary (κ → 0)")
print("----------------------------------------")
print("t    Δ          κ          FXI")
print("----------------------------------------")

for t in range(25):
    # effective contraction decreases as κ declines
    k_effective = max(k_base * kappa, 0.0)

    # apply structural update
    delta = E(delta, k_effective)
    fxi = 1.0 + alpha * delta

    # update κ (moves toward 0)
    kappa = max(kappa - k_degrade, 0.0)

    # print state
    print(f"{t:2d}   {delta: .6f}   {kappa: .6f}   {fxi: .6f}")

    if kappa == 0.0:
        print("\n>>> Viability boundary reached: κ = 0.0 (collapse edge)\n")
        break
