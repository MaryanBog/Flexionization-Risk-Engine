"""
FRE Demo #2 — Stress Test Scenario
(Before shock → Shock → Recovery)

This demo illustrates:
- stable Δ contraction,
- sudden structural shock,
- FRE-driven recovery back to stability.

Conceptual demonstration (independent of full simulator).
"""

import math

# structural deviation
delta = 0.25
k = 0.35       # contraction
alpha = 0.5    # FXI sensitivity

def E(d):
    """Contractive operator."""
    return k * d

print("FRE Demo #2 — Stress Test Scenario")
print("----------------------------------")

for t in range(10):
    delta = E(delta)
    fxi = 1.0 + alpha * delta
    print(f"t={t:2d}   Δ={delta:.5f}   FXI={fxi:.5f}")

# apply structural shock
shock = 2.0
delta *= shock

print("\n--- SHOCK OCCURS ---")
print(f"Δ jumps to {delta:.5f}\n")

# recovery phase
for t in range(10, 25):
    delta = E(delta)
    fxi = 1.0 + alpha * delta
    print(f"t={t:2d}   Δ={delta:.5f}   FXI={fxi:.5f}")
