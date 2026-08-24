# -*- coding: utf-8 -*-
"""
difficulty_evaluator.py
=======================
Objective, scientific, multi-dimensional difficulty evaluation engine
for Electrical Engineering Professional Licensing & Civil Service Exams.

Evaluates difficulty on a 1-5 scale based on 5 weighted dimensions:
1. Mathematical & Computational Complexity (25%)
2. Conceptual & Physical Abstraction (25%)
3. Multi-Step Derivation & Dependency Chain (20%)
4. Boundary Conditions & Tricky Constraints (15%)
5. Exam Score & Time Pressure Weight (15%)
"""

import re

def evaluate_question_difficulty(sid, topic, q_body="", score=20):
    full_text = f"{topic} {q_body}".lower()
    
    # -------------------------------------------------------------
    # 1. Math Score (1.0 ~ 5.0)
    # -------------------------------------------------------------
    math_s = 2.0
    
    # Level 5 Math (Advanced Numerical, Higher PDE, SVD, Non-linear Optimization)
    l5_math = [
        'svd', '奇異值', '狀態估計', '加權最小平方', '壞資料', '雅可比', '偏微分', 'pde', 
        '次同步諧振', '多機系統', '協調方程', '懲罰因數', '微增成本', '牛頓－拉夫遜', 
        '快速解耦', '李雅普諾夫', '弧閃'
    ]
    # Level 4 Math (Complex Variables, Residues, Eigenvalues/Diagonalization, 2nd-order ODE, Symmetric Components)
    l4_math = [
        '留數', '複變', '特徵值', '特徵向量', '對角化', '零空間', '二階非齊次', '二階線性', 
        '拉氏反轉換', '部分分式', '傅立葉級數', '對稱分量', '雙反應', '凸極', '四分裂', 
        '幾何均數', 'gmd', 'gmr', 'abcd參數', 'z參數', 'h參數', '轉移函數', '矩陣對角', 
        '諧波', 'thd', 'ieee 519', '短路容量', '非對稱'
    ]
    # Level 3 Math (1st-order ODE, Phasors, Complex Power, Matrices)
    l3_math = [
        '一階ode', '拉氏轉換', '行列式', '相量', '阻抗', '三要素', '二階rlc', '欠阻尼', 
        '臨界阻尼', '複數功率', '三相平衡', 'y-delta', '轉矩轉差率', '感應電動機', '等面積', 
        '戴維寧', '諾頓', '最大功率', '重疊定理'
    ]
    # Level 1 Math (Direct Algebraic, Single Formula, Ohm's Law)
    l1_math = [
        '歐姆定律', '純電阻', '直流穩態', '變壓器變比', '極數', '基本邏輯', '卡諾圖', 
        '功率因數改善', '分壓', '分流', '需量', '負載因數', '節點電壓', '網目', '單相二線'
    ]
    
    if any(k in full_text for k in l5_math):
        math_s = 5.0
    elif any(k in full_text for k in l4_math):
        math_s = 4.2
    elif any(k in full_text for k in l3_math):
        math_s = 3.0
    elif any(k in full_text for k in l1_math) and not any(k in full_text for k in (l4_math + l5_math)):
        math_s = 1.2
    else:
        math_s = 2.2
        
    # -------------------------------------------------------------
    # 2. Concept Score (1.0 ~ 5.0)
    # -------------------------------------------------------------
    concept_s = 2.0
    # Level 5 Concepts (Modern Dynamics, Control & Power Electronics Inverters, Safety Standard Design)
    l5_concept = [
        'pss', '電力系統穩定器', '低頻振盪', '小訊號穩定度', 'facts', 'statcom', 'svc', 
        'spwm死區', '空間向量', '雙軸凸極', 'ieee std 80', '接地網安全', '跨步電壓', 
        '接觸電壓', 'agc', '一次頻率響應', '行波反射', '波阻抗', '絕緣配合', '電弧閃絡', 'cmfb', '零空間'
    ]
    # Level 4 Concepts (Fault Analysis, Advanced Machines, Protection Coordination)
    l4_concept = [
        '單相接地故障', 'slg', '線間短路', '雙線接地', '2lg', '反時限', '保護協調', 
        '距離電驛', 'mho', '阻抗圓', '等面積準則', '臨界清除角', '差動放大器', 'cmrr', 
        'buck-boost', '全橋變流器', 'ccm', 'dcm', '自耦變壓器', '開路短路試驗', '零序等效', 
        '閘流體', '保護協調', 'tcc', '雙鼠籠', '凸極'
    ]
    # Level 3 Concepts (Standard Core Subject Principles)
    l3_concept = [
        '三相平衡', '互感', '同名端', '分激電動機', '串激電動機', '運算放大器', '主動濾波器', 
        'mosfet', 'bjt', '齊納二極體', '交流穩態', '戴維寧', '諾頓', '最大功率', '感應電動機', '諧振'
    ]
    # Level 1 Concepts
    l1_concept = [
        '直流電路', '基本邏輯閘', '理想變壓器', '純電阻', '純電感', '純電容', '照明', '點光源', '功率因數'
    ]
    
    if any(k in full_text for k in l5_concept):
        concept_s = 5.0
    elif any(k in full_text for k in l4_concept):
        concept_s = 4.2
    elif any(k in full_text for k in l3_concept):
        concept_s = 3.0
    elif any(k in full_text for k in l1_concept) and not any(k in full_text for k in (l4_concept + l5_concept)):
        concept_s = 1.2
    else:
        concept_s = 2.2
        
    # -------------------------------------------------------------
    # 3. Step Derivation & Sub-question Complexity
    # -------------------------------------------------------------
    sub_count = len(re.findall(r'(\([一二三四五六七八九十1-9]\)|\b[1-5]\.)', full_text))
    if sub_count >= 4:
        step_s = 5.0
    elif sub_count == 3:
        step_s = 4.0
    elif sub_count == 2:
        step_s = 2.8
    elif sub_count == 1:
        step_s = 1.8
    else:
        if len(full_text) > 160:
            step_s = 3.0
        elif len(full_text) > 80:
            step_s = 2.0
        else:
            step_s = 1.0

    # -------------------------------------------------------------
    # 4. Boundary & Constraint Traps
    # -------------------------------------------------------------
    tricky_words = [
        '開關切換', '初始電壓', '初始電流', '非零初始', 't=0', 't>0', 't1', '相依電源', 
        '受控源', '電流極限', '飽和', '非對稱', '接地電阻', '中性點接地', '雙開關', 
        '延時', 'zone 1', 'zone 2', '懲罰因數', '輸電損失', '壞資料', '臨界清除', 
        '熱極限', '非線性', '不平衡'
    ]
    tricky_m = sum(1 for w in tricky_words if w in full_text)
    if tricky_m >= 3:
        bound_s = 5.0
    elif tricky_m == 2:
        bound_s = 3.8
    elif tricky_m == 1:
        bound_s = 2.6
    else:
        bound_s = 1.0

    # -------------------------------------------------------------
    # 5. Score Weight
    # -------------------------------------------------------------
    score_m = re.search(r'（(\d+)\s*分）', full_text)
    if score_m:
        score = int(score_m.group(1))
    if score >= 30:
        weight_s = 5.0
    elif score >= 25:
        weight_s = 3.8
    elif score >= 20:
        weight_s = 2.8
    elif score >= 15:
        weight_s = 1.8
    else:
        weight_s = 1.0

    raw = 0.25 * math_s + 0.25 * concept_s + 0.20 * step_s + 0.15 * bound_s + 0.15 * weight_s

    # Scientific calibration thresholds
    if raw >= 3.30:
        stars = 5
    elif raw >= 2.80:
        stars = 4
    elif raw >= 2.20:
        stars = 3
    elif raw >= 1.75:
        stars = 2
    else:
        stars = 1

    return stars, round(raw, 2), {
        'math': round(math_s, 1),
        'concept': round(concept_s, 1),
        'step': round(step_s, 1),
        'boundary': round(bound_s, 1),
        'weight': round(weight_s, 1),
    }
