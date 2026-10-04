"""EE-113-02-4 independent check: full-bridge, centre-tapped secondary, BCM (symbolic).

Givens (official crop): Vs, S1..S4 full bridge (diagonals S1-S2, S3-S4), Np:Ns,
centre-tapped secondary (Vs1, Vs2), D1/D2, Lx, C || R. fs, D, BCM.
The stem defines D as the switch duty: each diagonal pair conducts D*Ts per period
(0 < D < 0.5, legs cannot shoot through); n_h = half-winding turns / Np.  If Ns is a half winding, n_h = Ns/Np;
if Ns is end-to-end, n_h = Ns/(2Np).
Method: build the rectified voltage over one full period (two pulses) and impose
zero average inductor voltage; BCM from current fall over the freewheel interval.
"""
import sympy as sp

Vs, D, R, fs, Lx, nh, Ns, Np = sp.symbols("V_s D R f_s L_x n_h N_s N_p", positive=True)
Vo = sp.symbols("V_o", positive=True)
Ts = 1 / fs
# (1) blocking voltage: when S1,S2 on, S3 and S4 each sit across the full bus
v_S3 = Vs - 0      # S3 spans bus+ to the leg midpoint pulled to bus-
v_S4 = Vs - 0
assert v_S3 == Vs and v_S4 == Vs

# (2) full-period volt-second balance with two rectified pulses
area = 2 * (nh * Vs - Vo) * D * Ts + (-Vo) * (Ts - 2 * D * Ts)
ratio = sp.solve(sp.Eq(area, 0), Vo)[0] / Vs
assert sp.simplify(ratio - 2 * D * nh) == 0
assert sp.simplify(ratio.subs(nh, Ns / Np) - 2 * D * Ns / Np) == 0
assert sp.simplify(ratio.subs(nh, Ns / (2 * Np)) - D * Ns / Np) == 0

# (3) BCM: per half-period, current rises from 0 and returns to 0; average = Io
Vo_s = 2 * D * nh * Vs
rise = (nh * Vs - Vo_s) * D * Ts / Lx
fall = Vo_s * (Ts / 2 - D * Ts) / Lx
assert sp.simplify(rise - fall) == 0
Lb = sp.solve(sp.Eq(fall / 2, Vo_s / R), Lx)[0]
assert sp.simplify(Lb - (1 - 2 * D) * R / (4 * fs)) == 0

# numeric spot check (illustrative): Vs=100, D=0.2, R=10, fs=20 kHz -> 75 uH
assert Lb.subs({D: sp.Rational(1, 5), R: 10, fs: 20000}) == sp.Rational(75, 10**6)
print("V_switch=Vs, Vo/Vs=2*D*n_h, Lx=(1-2D)R/(4fs)")
print("PASS EE-113-02-4")
