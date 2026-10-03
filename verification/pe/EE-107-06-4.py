"""EE-107-06-4: 10 HP (27 A) and 30 HP (78 A), 3-phase 220 V, continuous duty, rigid PVC conduit,
full-voltage start, class A, overcurrent protection 1.5 x full-load current.

The conductor ampacity table and the standard AT series are NOT in the stem; the named constants
mirror the note's 「條件與疑義」 and must be checked against the code tables.
"""
# ---- assumed table values ----
AMPACITY_PVC_CONDUIT_3W = {5.5: 30, 8: 40, 14: 55, 22: 70, 30: 90, 38: 100, 50: 120, 60: 150}   # mm2 -> A
STANDARD_AT = [15, 20, 30, 40, 50, 60, 75, 100, 125, 150, 175, 200, 225]
CONT = 1.25                    # continuous-duty conductor multiplier
OCP_MULT = 1.5                 # given in the stem
I10, I30 = 27.0, 78.0          # given

def conductor(required):
    return min(s for s, a in AMPACITY_PVC_CONDUIT_3W.items() if a >= required)

def at_round_up(required):
    return min(a for a in STANDARD_AT if a >= required)

req10, req30 = CONT * I10, CONT * I30
assert (req10, req30) == (33.75, 97.5)
assert conductor(req10) == 8 and conductor(req30) == 38         # boxed branch conductors
oc10, oc30 = OCP_MULT * I10, OCP_MULT * I30
assert (oc10, oc30) == (40.5, 117.0)
assert at_round_up(oc10) == 50 and at_round_up(oc30) == 125     # boxed branch AT

req_main = CONT * I30 + I10
assert req_main == 124.5
assert conductor(req_main) == 60                                  # boxed feeder conductor
oc_main = OCP_MULT * I30 + I10
assert oc_main == 144.0
assert at_round_up(oc_main) == 150                                # boxed feeder AT
# coordination: feeder AT must not exceed largest branch AT + other full-load current
assert 150 <= 125 + I10 + 1e-9
# conclusion is robust to the 38 mm2 table value but needs 50 mm2 < 124.5 A <= 60 mm2
assert AMPACITY_PVC_CONDUIT_3W[50] < req_main <= AMPACITY_PVC_CONDUIT_3W[60]
assert AMPACITY_PVC_CONDUIT_3W[30] < req30 <= AMPACITY_PVC_CONDUIT_3W[38]
print("PASS EE-107-06-4")
