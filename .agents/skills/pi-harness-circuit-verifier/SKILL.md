---
name: pi-harness-circuit-verifier
description: Deterministic modified nodal analysis gate for verifying complex electrical-engineering exam solutions.
---

# Pi Harness Circuit Verifier

本 skill 是題解 Solver 與 Verifier 之間的確定性驗算閘門，專門處理複雜線性電路。它不產生題意、不猜測元件連接，也不替代閱卷判斷；它只對已明確建模的電路求解並檢查方程殘差。

## 適用題型

- 多節點 KCL／節點電壓法
- 含獨立電壓源與電流源的 MNA
- 含相依電壓源（VCVS）的運算放大器與控制電路
- 複數相量、RLC 頻域阻抗與導納
- 需要獨立驗證節點電壓、支路電流或電壓約束的題解

## 強制流程

1. Solver 先建立節點編號、參考地、元件方向與符號定義。
2. 將電路轉成 JSON，交由 `scripts/tools/circuit_verifier.py solve` 求解。
3. 檢查 `constraints_ok`、`max_kcl_residual` 與 `max_constraint_residual`。
4. 將驗算結果與 Solver 的解析答案逐項比對；不一致時標記 `UNVERIFIED`，不得寫入「已驗證」題解。
5. 對相量題另外檢查實部／虛部與極座標轉換，對功率題檢查功率平衡。

## JSON 介面

```json
{
  "node_count": 2,
  "passive_elements": [
    {"type": "R", "n1": 2, "n2": 1, "value": 1000},
    {"type": "C", "n1": 1, "n2": 0, "value": 0.000001}
  ],
  "current_sources": [],
  "voltage_sources": [
    {"n_plus": 2, "n_minus": 0, "voltage": 12}
  ],
  "controlled_voltage_sources": [],
  "frequency_hz": 1000
}
```

節點 `0` 永遠代表參考地。獨立電流源方向為 `n_plus -> n_minus`；VCVS 約束為 `V(out+) - V(out-) = gain * (V(control+) - V(control-))`。

## 阻擋條件

- MNA 矩陣奇異或欠約束：停止並回報模型錯誤。
- KCL 或電壓約束殘差超過 `1e-9`：不得標記通過。
- 元件方向、參考地或單位未明確：先回到題意建模，不可直接求數值。
- SPICE／數值結果與解析推導不一致：保留兩份結果與差異，交由獨立 Verifier 重新檢查。

## 指令

```bash
python3 scripts/tools/circuit_verifier.py solve '<circuit_json>'
```

這個驗算器保持零後端、可離線執行，不會修改 `dashboard-data.js`、`solutions-bundle.js` 或前端 bundle。
