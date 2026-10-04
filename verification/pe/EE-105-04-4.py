"""EE-105-04-4 (descriptive/quantitative): synchronous motor at 0.8 leading, raise pf to 1.0 by changing I_f.
Sample per-unit machine (Xs=1 pu, V=1 pu, P=0.8 pu) -- values are illustrative, not from the stem."""
import numpy as np

V, Xs, P = 1.0, 1.0, 0.8
def ef(pf_angle_deg):                      # leading: current leads V by +angle
    I = P / (V * np.cos(np.radians(pf_angle_deg)))
    Ia = I * np.exp(1j * np.radians(pf_angle_deg))
    return V - 1j * Xs * Ia, abs(Ia)       # motor: Ef = V - jXs Ia
E_lead, I_lead = ef(np.degrees(np.arccos(0.8)))
E_unity, I_unity = ef(0.0)
assert abs(E_lead) > abs(E_unity)          # over-excited at leading pf -> reduce If to reach unity
assert I_unity < I_lead                    # armature current minimum at unity pf
# constant power: Ef sin(delta) is constant (P = V*Ef*sin(delta)/Xs)
assert abs(abs(E_lead) * np.sin(-np.angle(E_lead)) - abs(E_unity) * np.sin(-np.angle(E_unity))) < 1e-9
print("PASS EE-105-04-4 (descriptive)")
