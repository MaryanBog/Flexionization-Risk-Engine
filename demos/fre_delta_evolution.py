"""
FRE Demo #1 — Delta Evolution (Δ → E(Δ) → Δₜ₊₁)

This demo shows:
- how structural deviation Δ contracts over time,
- how FXI responds,
- how stability improves under the FRE contraction operator.

This is a conceptual demonstration, independent of the full simulator.
"""

import math

# initial structural deviation
delta = 0.4
k = 0.35      # contraction factor (0 < k < 1)
alpha = 0.5   # FXI sensitivity

def E(d):
    """FRE contraction operator."""
    return k * d

print("FRE Demo #1 — Δ Evolution")
print("-------------------------")

for t in range(20):
    delta = E(delta)
    fxi = 1.0 + alpha * delta
    print(f"t={t:2d}   Δ={delta:.5f}   FXI={fxi:.5f}")
