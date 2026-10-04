"""EE-108-06-2: arc-furnace voltage dip at the 69 kV measuring point and series reactor.

Givens (crop): source 2500 MVA; measuring point on the 69 kV source side before the main
transformer; 69 kV line Z_L=j0.405 ohm; main transformer 30 MVA 69/11.4 kV Z=7 %;
furnace transformer 15 MVA 11.4 kV/300 V Z=6 %; furnace 12.5 MVA Z_F=8 %; limit 1.5 %.
Base: main transformer rating 30 MVA.  Constant-impedance divider model.
"""
SB = 30.0          # MVA
ZB69 = 69.0**2 / SB
ZB114 = 11.4**2 / SB

XS = SB / 2500.0
XL = 0.405 / ZB69
XT1 = 0.07
XT2 = 0.06 * SB / 15.0
XF = 0.08 * SB / 12.5
assert abs(ZB69 - 158.7) < 1e-9 and abs(ZB114 - 4.332) < 1e-9
for got, want in ((XS, 0.012), (XL, 0.002552), (XT1, 0.07), (XT2, 0.12), (XF, 0.192)):
    assert abs(got - want) / want < 5e-4

X_down = XL + XT1 + XT2 + XF
dip = XS / (XS + X_down)
assert abs(X_down - 0.384552) < 1e-6
assert abs(dip * 100 - 3.0261) / 3.0261 < 5e-4              # boxed (二)

XR = XS / 0.015 - (XS + X_down)
assert abs(XR - 0.403448) < 1e-5
XR_ohm = XR * ZB114
assert abs(XR_ohm - 1.748) / 1.748 < 5e-4                    # boxed (三)
assert abs(XS / (XS + X_down + XR) - 0.015) < 1e-12

# independent check in ohms on the 11.4 kV side (all impedances referred to 11.4 kV)
k = (11.4 / 69.0) ** 2
src = 69.0**2 / 2500.0 * k
line = 0.405 * k
t1 = 0.07 * 11.4**2 / 30.0
t2 = 0.06 * 11.4**2 / 15.0
furn = 0.08 * 0.3**2 / 12.5 * (11.4 / 0.3) ** 2
down = line + t1 + t2 + furn
assert abs(src / (src + down) - dip) < 1e-9
assert abs((src / 0.015 - src - down) - XR_ohm) < 1e-6
print("PASS EE-108-06-2")
