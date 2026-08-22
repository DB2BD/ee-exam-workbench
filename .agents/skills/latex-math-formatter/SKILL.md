---
name: latex-math-formatter
description: >-
  專門用於工程數學、電機電路、矩陣、微積分與工程物理公式的標準 LaTeX 格式化與排版優化技能。
  嚴格遵循 KaTeX / MathJax / Obsidian / GitHub Markdown 相容規範。
---

# 📐 LaTeX 數學與電機公式標準排版技能 (LaTeX Math Formatter)

本 Skill 專門規範並執行電機工程技師考試相關的所有數學式、相量式、矩陣式與電氣物理量單位的 LaTeX 排版標準。

---

## 📌 核心排版規則

### 1. 矩陣與聯立方程 (Matrices & Piecewise)
- **矩陣一律使用 `bmatrix`**：
  $$\mathbf{A} = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$$
- **分段函數一律使用 `cases`**：
  $$f(t) = \begin{cases} 1, & 0 \le t < T_0 \\ 0, & \text{其他} \end{cases}$$

### 2. 電氣單位標準格式（使用 `\text{}` 或 `\Omega`）
| 物理量 | 規範 LaTeX 寫法 | 錯誤寫法（禁止） |
| :--- | :--- | :--- |
| 電阻 (歐姆) | `$10\ \Omega$`, `$10\text{ k}\Omega$` | `10 歐姆`, `10ohm`, `10 \Omega` (破字) |
| 電感 (亨利) | `$10\text{ mH}$`, `$2\text{ H}$` | `10mH`, `10 mH` (斜體) |
| 電容 (法拉) | `$1\ \mu\text{F}$`, `$10\text{ pF}$` | `1uF`, `1 μF` |
| 頻率 (赫茲) | `$60\text{ Hz}$`, `$100\text{ kHz}$` | `60Hz`, `60 Hz` |
| 角頻率 | `$\omega = 377\text{ rad/s}$` | `w=377rad/s` |
| 功率 (實/虛/視在) | `$100\text{ kW}$`, `$50\text{ kvar}$`, `$100\text{ MVA}$` | `100kW`, `50kVAR` |
| 相量角度 | `$\mathbf{V} = 110\angle 30^\circ\text{ V}$` | `110∠30o`, `110∠30度` |

### 3. 微積分與微分方程
- 導數符號：$\frac{dy}{dx}, \frac{d^2y}{dx^2}, y''(t) + 4y'(t) + 4y(t) = 0$。
- 偏導數符號：$\frac{\partial u}{\partial x}, \nabla \times \mathbf{F}$。
- 環路積分：$\oint_C f(z) dz$。
- 散度定理面積分：$\iint_S \mathbf{F} \cdot \mathbf{n} dA$。
