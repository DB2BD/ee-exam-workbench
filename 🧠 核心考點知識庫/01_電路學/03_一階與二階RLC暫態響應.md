# ⚡ 電路學 核心考點 03 — 一階與二階 RLC 暫態響應

## 📌 核心解題 SOP
1. **開關切換連續性定律**：
   i_L(0^+) = i_L(0^-), \quad v_C(0^+) = v_C(0^-)
2. **一階電路步階響應三要素公式**：
   x(t) = x(\infty) + [x(0^+) - x(\infty)] e^{-t/\tau}, \quad t \ge 0
   - $RC$ 電路時間常數：$\tau = R_{th} C$
   - $RL$ 電路時間常數：$\tau = \frac{L}{R_{th}}$
3. **二階 RLC 電路特徵根與響應分類**：
   - 特徵方程式：$s^2 + 2\alpha s + \omega_0^2 = 0 \implies s_{1,2} = -\alpha \pm \sqrt{\alpha^2 - \omega_0^2}$
   - **串聯 RLC**：$\alpha = \frac{R}{2L}, \quad \omega_0 = \frac{1}{\sqrt{LC}}$
   - **並聯 RLC**：$\alpha = \frac{1}{2RC}, \quad \omega_0 = \frac{1}{\sqrt{LC}}$
   - **阻尼狀態判定**：
     - $\alpha > \omega_0$：**過阻尼（Overdamped）**，$x(t) = A_1 e^{s_1 t} + A_2 e^{s_2 t} + x(\infty)$
     - $\alpha = \omega_0$：**臨界阻尼（Critically Damped）**，$x(t) = (A_1 + A_2 t) e^{-\alpha t} + x(\infty)$
     - $\alpha < \omega_0$：**欠阻尼（Underdamped）**，$x(t) = e^{-\alpha t} (A_1 \cos\omega_d t + A_2 \sin\omega_d t) + x(\infty)$，其中 $\omega_d = \sqrt{\omega_0^2 - \alpha^2}$。

---

## 🎯 歷屆技師高頻出題年份
- **114 年 第三題**：開關切換一階/二階暫態初值與時域表示式。
- **112 年 第三題**：二階並聯 RLC 電路欠阻尼暫態響應。
- **107 年 第二題**：一階 RL 電路脈衝激勵響應。
