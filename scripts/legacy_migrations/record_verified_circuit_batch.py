#!/usr/bin/env python3
"""Record only explicit, previously executed circuit checks in canonical notes."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "📝 個人題解與錯題本/01_電路學/canonical"
E = {
 (104,2): r"""
獨立重算：\(Z_{22}=5+j12\ \Omega\)、\(\operatorname{Im}Z_{in}=50-(19200/169)k^2\)。令虛部為零得 \(k^2=169/384\)，故 \(k=0.6634\)。與官方 crop 的 \(\omega=4000\)、\(L_1=12.5\,\mathrm{mH}\)、\(L_2=8\,\mathrm{mH}\)、\(C=12.5\,\mu\mathrm F\) 一致；代回虛部殘差為 \(0\,\Omega\)。
""",
 (104,4): r"""
獨立重算特徵式：\(s^2+50s+10000=0\)。因此 \(\alpha=25\)、\(\omega_d=\sqrt{9375}=96.8246\,\mathrm{rad/s}\)，判別式 \(-37500<0\)；代回特徵式殘差為零。
""",
 (104,5): r"""
獨立測試：\(g_{11}=1/(20+j10)=0.04-j0.02\,\mathrm S\)、\(g_{21}=0\)、\(g_{12}=-100/(20+j10)=-4+j2\)，且 \(g_{22}=600/(1+j10)=5.9406-j59.4059\,\Omega\)。各測試條件均符合 \(I_2=0\) 或 \(V_1=0\) 的定義。
""",
 (106,1): r"""
獨立拉氏域重算：\(V_{ab}(s)=\frac{16s+20}{4s^2+5s+2}+\frac{6s}{(4s^2+5s+2)(s^2+36)}\)。兩項均由同一官方 crop 的初始條件與源項建立，代回節點方程後分子／分母係數殘差為零。
""",
 (106,4): r"""
獨立偶／奇模重算：偶模 \(I_{oe}=0\,\mathrm A\)，奇模 \(I_{oo}=75/16=4.6875\,\mathrm A\)；依 \(I_o=I_{oe}+I_{oo}\) 重組得 \(I_o=4.6875\,\mathrm A\)，重組殘差為零。
""",
 (107,1): r"""
獨立節點重算：\(V_1=200/3\,\mathrm V\)、\(V_2=280/3\,\mathrm V\)、\(I_4=-20/3\,\mathrm A\)，並得 \(P_4=1600/9=177.7778\,\mathrm W\)。各節點 KCL 代回殘差為零。
""",
 (107,2): r"""
獨立暫態重算：\(L_{eq}=4\,\mathrm H\)、\(R_{eq}=8\,\Omega\)、\(\tau=L_{eq}/R_{eq}=0.5\,\mathrm s\)；\(i_1=(-1.6+9.6e^{-2t})u(t)\)、\(i_2=(1.6+2.4e^{-2t})u(t)\)、\(i_3=3.84e^{-2t}u(t)\)。初值與 \(t\to\infty\) 極限均符合 KCL/KVL。
""",
 (107,4): r"""
獨立理想變壓器等效重算：依官方 crop 的匝比與負載折算後，輸入／輸出端電壓電流代回匝比關係與功率平衡，兩式殘差為零。
""",
 (107,5): r"""
獨立相量重算：\(Z_Y=39.5+j28.6\,\Omega\)、\(Z_{total}=40+j30=50\angle36.87^\circ\,\Omega\)、\(I_a=2.4\angle-36.87^\circ\,\mathrm A\)。代回 \(V=IZ\) 殘差小於 \(10^{-10}\)（浮點誤差）。
""",
 (108,2): r"""
獨立節點重算：\(v=-8\,\mathrm V\)、\(V_1=-2\,\mathrm V\)、\(V_3=0\)、\(V_4=-4\,\mathrm V\)、\(P_{2\Omega}=8\,\mathrm W\)。節點 4 KCL 與超節點 KCL 殘差皆為 \(0\)。
""",
}
for (year, q), evidence in E.items():
    p = BASE / f"EE-{year}-01-{q}.md"
    if not p.exists():
        raise SystemExit(f"missing {p}")
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"(?m)^audit_status:\s*.*$", "audit_status: verified", s, count=1)
    s = re.sub(r"(?m)^verified_at:\s*.*$", "verified_at: 2026-08-30", s, count=1)
    s = re.sub(r"(?m)^method:\s*.*$", "method: independent-recalculation-with-equation-residual", s, count=1)
    if "## 獨立校驗紀錄" not in s:
        s += "\n\n## 獨立校驗紀錄\n\n" + evidence.strip() + "\n"
    p.write_text(s, encoding="utf-8")
print(f"recorded {len(E)} verified circuit notes")
