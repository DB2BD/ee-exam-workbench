"""EE-111-06-4 (table-dependent): four continuously running motors, 220 V 3-phase, metal conduit.

Stem givens: 20 HP welder, 20 HP compressor, 10 HP, 8 HP; PF 0.85 lag; code letter B;
max OCP = 1.8 x rated current; metal conduit.  Efficiency and code tables are NOT in the stem.
Named constants below mirror the note's 「條件與疑義」: reference-book FLC (1 HP ~ 1 kVA),
conduit ampacities and the standard AT series are assumptions to be checked against the code tables.
"""
import numpy as np

V = 220.0
HP = {"weld20": 20, "comp20": 20, "ac10": 10, "lathe8": 8}
# ---- assumed table values (mirror 「條件與疑義」) ----
KVA_PER_HP = 1.0                                   # reference book: 1 HP ~ 1 kVA input
AMPACITY_CONDUIT_3W = {5.5: 30, 8: 40, 14: 55, 22: 70, 80: 150, 100: 170, 125: 220}   # mm2 -> A; 80/100 assumed, 125 = book value
FEEDER_CONDUCTOR_NOT_BELOW_AT = True               # reference-book design rule (not a stem given)
STANDARD_AT = [15, 20, 30, 40, 50, 60, 70, 75, 100, 125, 150, 175, 200, 225]
OCP_MAX_MULT = 1.8                                 # given in stem
CONT_MULT = 1.25

flc = {k: KVA_PER_HP * hp * 1e3 / (np.sqrt(3) * V) for k, hp in HP.items()}
assert abs(flc["comp20"] - 52.49) < 0.005 and abs(flc["ac10"] - 26.24) < 0.005 and abs(flc["lathe8"] - 20.99) < 0.005

def smallest_conductor(req):
    return min(s for s, a in AMPACITY_CONDUIT_3W.items() if a >= req)

# branches: conductor >= 1.25 FLC; OCP = conductor ampacity, checked against 1.25 FLC <= OCP <= 1.8 FLC
branch = {}
for k in ("comp20", "ac10", "lathe8"):
    size = smallest_conductor(CONT_MULT * flc[k])
    ocp = AMPACITY_CONDUIT_3W[size]
    assert ocp in STANDARD_AT and CONT_MULT * flc[k] <= ocp <= OCP_MAX_MULT * flc[k]
    branch[k] = (size, ocp)
assert branch == {"comp20": (22, 70), "ac10": (8, 40), "lathe8": (5.5, 30)}   # boxed 22/8/5.5 mm2, 70/40/30 AT

# feeder: ampacity >= 1.25 I_max + sum(others); OCP <= 1.8 I_max + sum(others), largest standard below
others = sum(flc.values()) - flc["comp20"]
req_feeder = CONT_MULT * flc["comp20"] + others
ocp_feeder_max = OCP_MAX_MULT * flc["comp20"] + others
assert abs(req_feeder - 165.33) < 0.01 and abs(ocp_feeder_max - 194.2) < 0.05
at_feeder = max(a for a in STANDARD_AT if a <= ocp_feeder_max)
assert at_feeder == 175                                             # boxed 175 AT / 225 AF
main_req = max(req_feeder, at_feeder) if FEEDER_CONDUCTOR_NOT_BELOW_AT else req_feeder
main_size = smallest_conductor(main_req)
assert main_size == 125 and AMPACITY_CONDUIT_3W[125] == 220          # boxed 125 mm2 (220 A)
assert AMPACITY_CONDUIT_3W[100] < at_feeder <= AMPACITY_CONDUIT_3W[125]
# branch in 「條件與疑義」: without the book rule 165.3 A -> 100 mm2; with 100 mm2 >= 175 A -> 100 mm2
assert smallest_conductor(req_feeder) == 100
assert min(s for s, a in {**AMPACITY_CONDUIT_3W, 100: 175}.items() if a >= at_feeder) == 100
assert at_feeder >= max(o for _, o in branch.values())

# independent cross-check from first principles: P = sqrt3 V I pf eta  ->  1 kVA/HP <=> eta*pf = 0.746
eta_implied = 0.746 / 0.85
assert abs(20 * 746 / (np.sqrt(3) * V * 0.85 * eta_implied) - flc["comp20"]) < 1e-9
# eta-parameterised strings kept in 「條件與疑義」 (eta = 1, pf 0.85)
unit = 746 / (np.sqrt(3) * V * 0.85)
i20, i10, i8 = 20 * unit, 10 * unit, 8 * unit
assert f"{i20:.4f}" == "46.0645" and f"{i10:.4f}" == "23.0323" and f"{i8:.4f}" == "18.4258"
assert f"{1.25*i20+i20+i10+i8:.4f}" == "145.1033" and f"{1.8*i20+i20+i10+i8:.4f}" == "170.4387"
# table-B branch (54/28/22 A)
assert abs(1.25 * 54 + 54 + 28 + 22 - 171.5) < 1e-9 and abs(1.8 * 54 + 54 + 28 + 22 - 201.2) < 1e-9
print("PASS EE-111-06-4")
