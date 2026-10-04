"""EE-106-04-2: 2400/240 V, 50 kVA, 60 Hz two-winding transformer, eta = 98 % at full load unity pf.
Reconnected as autotransformer 2400 V -> 2640 V."""
Vh_w, Vx_w, S, eta = 2400.0, 240.0, 50e3, 0.98
Vin, Vout = 2400.0, 2640.0
assert abs(Vin + Vx_w - Vout) < 1e-9        # 240 V winding aids the 2400 V winding
Is_rated = S / Vx_w                          # series (240 V) winding, 208.33 A
Ic_rated = S / Vh_w                          # common (2400 V) winding, 20.83 A
I_out = Is_rated                              # load current flows through the series winding
I_in = Vout * I_out / Vin                     # ideal
assert abs((I_in - I_out) - Ic_rated) < 1e-9  # common winding current = I_in - I_out = rated
S_auto = Vout * I_out
assert abs(S_auto - 550e3) < 1e-6
loss = S / eta - S                            # 1.0204 kW, unchanged by the reconnection
P_out = S_auto * 1.0
eta_auto = P_out / (P_out + loss)
assert abs(eta_auto - 0.9981) / 0.9981 <= 0.005
# independent: efficiency from loss fraction
assert abs((1 - eta_auto) - loss / (P_out + loss)) < 1e-12
assert abs(S_auto / S - 11) < 1e-9
print(f"S_auto={S_auto/1e3:.1f} kVA loss={loss:.2f} W eta={eta_auto*100:.4f}% Iin={I_in:.2f}")
print("PASS EE-106-04-2")
