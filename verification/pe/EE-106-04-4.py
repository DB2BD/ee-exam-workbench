"""EE-106-04-4: 3-phase induction motor 230 V, 60 Hz, 25 hp; draws 60 A at pf 0.866 lagging.
Stator copper 850 W, core 450 W, rotor copper 1050 W, rotational 500 W."""
import math
VL, I, pf = 230.0, 60.0, 0.866
Pcu1, Pcore, Pcu2, Prot = 850.0, 450.0, 1050.0, 500.0
Pin = math.sqrt(3) * VL * I * pf
Pag = Pin - Pcu1 - Pcore
Pconv = Pag - Pcu2
Pout = Pconv - Prot
eta = Pout / Pin
assert abs(Pin - 20700) / 20700 <= 0.005
assert abs(Pout - 17850) / 17850 <= 0.005
assert abs(Pout / 746 - 23.93) / 23.93 <= 0.005
assert abs(eta - 0.8623) / 0.8623 <= 0.005
# independent: total-loss route and rotor-copper/slip consistency
assert abs(Pin - (Pout + Pcu1 + Pcore + Pcu2 + Prot)) < 1e-9
s = Pcu2 / Pag
assert abs(Pconv - (1 - s) * Pag) < 1e-9
print(f"Pin={Pin:.1f} Pag={Pag:.1f} Pconv={Pconv:.1f} Pout={Pout:.1f} W = {Pout/746:.3f} hp eta={eta*100:.3f}% s={s:.4f}")
print("PASS EE-106-04-4")
