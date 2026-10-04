"""EE-105-02-4 independent check: nonlinear load, v=100 sin(wt), i=7+12 sin(wt+30)+5 sin(3wt+60).

Method: sample one period numerically; P=mean(v i), Vrms/Irms by RMS, PF=P/(Vrms Irms);
harmonics separated with an FFT for the distortion factor and THD.
"""
import numpy as np

N = 4096
t = np.arange(N) / N * 2 * np.pi
v = 100 * np.sin(t)
i = 7 + 12 * np.sin(t + np.radians(30)) + 5 * np.sin(3 * t + np.radians(60))
P = np.mean(v * i)
Vrms, Irms = np.sqrt(np.mean(v**2)), np.sqrt(np.mean(i**2))
PF = P / (Vrms * Irms)
spec = np.fft.rfft(i) / N
I1 = abs(spec[1]) * 2 / np.sqrt(2)
DF = I1 / Irms
THD = np.sqrt(Irms**2 - I1**2) / I1
# leading: fundamental current phase relative to voltage
lead = np.degrees(np.angle(spec[1] / np.fft.rfft(v)[1]))


def close(x, y, tol=0.005):
    return abs(x - y) / abs(y) <= tol


assert close(P, 300 * np.sqrt(3)) and close(P, 519.62)
assert close(Irms, np.sqrt(133.5)) and close(PF, 0.6360, 0.001)
assert close(DF, 0.7344, 0.001) and close(THD, 0.9242, 0.001)
assert abs(lead - 30) < 1e-6
assert close(THD, np.sqrt(1 / DF**2 - 1))
print(f"P={P:.2f} W PF={PF:.4f} DF={DF:.4f} THD={THD:.4f} lead={lead:.1f} deg")
print("PASS EE-105-02-4")
