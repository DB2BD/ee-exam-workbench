# PE `needs_manual_review` evidence report

Investigation date: 2026-09-05 (Asia/Taipei)

## Scope and decision rule

This report covers the 17 PE records whose current audit status is `needs_manual_review` in `data/pe-solution-audit.json`. The result is deliberately conservative: a question is **uniquely verifiable** only when the local authoritative evidence fixes the topology, parameters, interpretation, and any graph reading needed for the requested answer. A conditional calculation, a stable partial result, or a plausible textbook assumption is not a unique verification and is not an upgrade.

Evidence used was restricted to the local dashboard/provenance data, canonical solution Markdown, PE audit manifest, crop manifest, and the local manual-review index. `reports/public-solution-sources.md` was checked only to confirm that its public links are explicitly secondary and cannot resolve an official-data gap; those links were not used as authority.

Source references below use local file paths and line anchors:

- **AUD** — `data/pe-solution-audit.json`: QID, method, status, and canonical link.
- **DASH** — `dashboard-data.js`: serialized PE record, official crop map, and `SOLUTION_REVIEW_METADATA` evidence/action.
- **CROP** — `data/pe-question-crops.json`: official PDF path, PDF SHA-256, page/crop rectangle, and crop-boundary metadata.
- **CAN** — the QID-specific canonical Markdown front matter and its review evidence/action.
- **IDX** — `reports/manual-review-index.md`: current 17-question index and conservative-review policy.

The crop paths and PDF paths below were also checked for existence. All 17 canonical files, crops, and source PDFs are present.

## Status snapshot

`data/pe-solution-audit.json` reports `questions=256`, `verified=239`, `needs_manual_review=17`, `suspected_error=0`, and `not_attempted=0`. The manual-review index independently states the same total and says that missing parameters, graph estimation, or source conflicts must not be upgraded to `verified` until resolved (`reports/manual-review-index.md:L1-L7`).

## Findings by question

### EE-104-06-5 — Industrial distribution, 104 Q5

- **Current status:** `needs_manual_review`; canonical disposition `power_factor_parameterized`; chapter: harmonic equivalent circuit and tuned capacitors. The dashboard record has a dedicated canonical solution and the same official crop path (`dashboard-data.js:L5812`, `dashboard-data.js:L5900`, `dashboard-data.js:L8608-L8614`; `data/pe-solution-audit.json:L3582-L3595`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/104年/104年_電機工程技師_工業配電.pdf`, SHA-256 `f0a6bffd97824f40f312adeb45d55dcc32d4fc3433a2a31479701849839474c2`; crop `PE_104年_工業配電_Q05.png`, file page 2, rectangle `[0,214.03,729,1014]`, `pdf_text_sequence` / `text_sequence` (`CROP:L7-L102`). The crop and canonical evidence fix 380 V, 250 MVA, 2 MVA transformer, 400/200 kvar capacitors, and 6% reactors, and show a parameterized fifth-harmonic back-substitution (`CAN:L21-L22` and front matter `L12-L14`).
- **Uniquely verifiable:** **No for the requested numerical outputs.** The network/topology and conditional back-substitution are available, but the official question does not say whether 500 kW is AC input power or DC output, does not give fundamental-frequency power factor or efficiency, and does not define the denominator of “20% rated current.”
- **Blocker / precise next step:** `missing_parameter`. Resolve the 500 kW power-side definition, obtain/explicitly state `pf_1` and efficiency `η`, and define whether rated current means AC fundamental, total AC RMS, or DC current. Until then retain the parameterized branches.
- **Recommended classification:** retain `needs_manual_review`; `power_factor_parameterized` (do not classify as `verified`).

### EE-106-06-2 — Industrial distribution, 106 Q2

- **Current status:** `needs_manual_review`; disposition `source_per_conductor_line_line_main_model`; chapter: short-circuit current, symmetrical components, and breaker rating (`dashboard-data.js:L4642`, `dashboard-data.js:L6018`, `dashboard-data.js:L8569-L8575`; `data/pe-solution-audit.json:L2854-L2867`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/106年/106年_電機工程技師_工業配電.pdf`, SHA-256 `76df3b1f0f1afeb76d51971956b74bdd1ce147874bca6baf3cc65e66ea1eb0a0`; crop `PE_106年_工業配電_Q02.png`, file page 1, rectangle `[0,309.01,729,596.09]`, `pdf_text_sequence` / `text_sequence` (`CROP:L1368-L1397`). The crop fixes F at the left 110 V conductor-to-neutral point and shows the 380 V two-phase primary; the canonical records a main per-conductor round-trip model plus alternative branches and an independent asymmetry calculation (`CAN:L21-L22` and front matter `L12-L14`).
- **Uniquely verifiable:** **No for the complete requested answer.** The fault topology is fixed by the crop, and conditional symmetrical-current calculations are reproducible; the numerical result is not unique because the impedance’s “per conductor” versus “round trip” meaning is unresolved, and non-symmetrical current also needs fault angle, observation time, and system frequency.
- **Blocker / precise next step:** `official_wording_ambiguity`. Confirm from the authoritative question context whether the stated impedance already includes the complete path; specify fault angle, observation time, and frequency for the non-symmetrical current. Do not collapse the listed branches.
- **Recommended classification:** retain `needs_manual_review`; `source_per_conductor_line_line_main_model`.

### EE-107-06-2 — Industrial distribution, 107 Q2

- **Current status:** `needs_manual_review`; disposition `rated_current_branches`; chapter: motor-feeder voltage drop and conductor length (`dashboard-data.js:L4090`, `dashboard-data.js:L6080`, `dashboard-data.js:L8576-L8586`; `data/pe-solution-audit.json:L2532-L2545`; `CAN:L2-L17`).
- **Available source evidence:** official PDF `依年度分類/107年/107年_電機工程技師_工業配電.pdf`, SHA-256 `f8894976cb323b7cad2274f9556660a133378a4410e61b952d6387764cdc75a5`; crop `PE_107年_工業配電_Q02.png`, file page 1, rectangle `[0,472.45,595.22,628.97]`, `pdf_text_sequence` / `text_sequence` (`CROP:L2053-L2082`). The crop/canonical fix 100 HP, 220 V, 0.85 lagging power factor, 100 mm² copper, 120 m, and the line impedance. The local canonical evidence records current branches, including the present table’s 238 A value and a 250 A alternative, but notes that the question does not supply the applicable historical table, nameplate, or efficiency (`CAN:L12-L16`).
- **Uniquely verifiable:** **No.** Voltage-drop arithmetic is reproducible once current is selected, but the authoritative local evidence does not uniquely determine the 100 HP full-load current under the relevant historical rule/nameplate basis.
- **Blocker / precise next step:** `missing_parameter`. Locate the 107-year applicable full-load-current table or the motor nameplate/efficiency; then recompute the voltage drop and maximum length using that single evidenced current. The local public mirror is expressly not sufficient to resolve this gap (`reports/public-solution-sources.md:L9-L9`).
- **Recommended classification:** retain `needs_manual_review`; `rated_current_branches`.

### EE-110-06-5 — Industrial distribution, 110 Q5

- **Current status:** `needs_manual_review`; disposition `conditional_numeric`; chapter: plant substation short-circuit capacity and motor subtransient contribution (`dashboard-data.js:L2606`, `dashboard-data.js:L6258`, `dashboard-data.js:L8594-L8600`; `data/pe-solution-audit.json:L1580-L1593`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/110年/110年_電機工程技師_工業配電.pdf`, SHA-256 `4e667e52813810e5043630074264b7862d938d00d329683984a245011f3af9a4`; crop `PE_110年_工業配電_Q05.png`, file page 3, rectangle `[0,356.34,595.22,824]`, `pdf_text_sequence` / `text_sequence` (`CROP:L3930-L4016`). The crop fixes the 1500 MVA source short-circuit capacity, F1 network, and three motor branches. The canonical records parameterized motor contributions and keeps the 100 MVA common base visibly identified as a solving choice rather than an official datum (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** The network is available, but the three motors’ efficiency/power factor or rated MVA and the meaning of `K=1.6` (RMS asymmetry multiplier versus peak multiplier) are not uniquely fixed.
- **Blocker / precise next step:** `missing_parameter`. Supply the motor ratings/efficiency and power factor (or rated MVA), establish the intended common base, and confirm the definition of `K=1.6` before selecting one instantaneous-capacity result.
- **Recommended classification:** retain `needs_manual_review`; `conditional_numeric`.

### EE-111-06-1 — Industrial distribution, 111 Q1

- **Current status:** `needs_manual_review`; disposition `graph_estimate`; chapter: instrument transformers and CT burden error (`dashboard-data.js:L1998`, `dashboard-data.js:L6308`, `dashboard-data.js:L8601-L8607`; `data/pe-solution-audit.json:L1202-L1215`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_工業配電.pdf`, SHA-256 `53a7db6996da137566fc7ef09444b0d9626812b7dd47c9c7ddfa9174be507feb`; crop `PE_111年_工業配電_Q01.png`, file page 1, rectangle `[0,241.97,595.22,824]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4541-L4551`). The crop includes the CT equivalent circuit, excitation curve, 100/5 ratio, `Z'=0.082 Ω`, and burden values 0.8/3.0 Ω. The canonical converts the graph to the common equation and records approximate intersections and the relay threshold check (`CAN:L12-L14`, `CAN:L21-L22`).
- **Uniquely verifiable:** **No for exact graph-read values.** The governing equation and qualitative threshold conclusion are supported, but the two intersections are graph estimates, with the 3.0 Ω point near the knee; exact values/precision cannot be verified from the available crop.
- **Blocker / precise next step:** `graph_estimate`. Inspect the official original page and crop and confirm only defensible significant-figure intervals (`I_e=0.15–0.25 A` and `2.2–2.8 A`) plus the `I'≥8 A` / `I'<8 A` threshold conclusion. Do not promote a graph center estimate to an exact answer.
- **Recommended classification:** retain `needs_manual_review`; `graph_estimate`.

### EE-111-06-2 — Industrial distribution, 111 Q2

- **Current status:** `needs_manual_review`; disposition `conditional_numeric`; chapter: synchronous-motor full-voltage starting and voltage variation (`dashboard-data.js:L2018`, `dashboard-data.js:L6310`, `dashboard-data.js:L8615-L8621`; `data/pe-solution-audit.json:L1216-L1229`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_工業配電.pdf`, SHA-256 `53a7db6996da137566fc7ef09444b0d9626812b7dd47c9c7ddfa9174be507feb`; crop `PE_111年_工業配電_Q02.png`, file page 2, rectangle `[0,29.51,595.22,197.87]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4541-L4570`). The crop fixes 69/3.3 kV, receiving-bus short-circuit capacity, transformer impedance, motor power, starting-current multiple, and starting power factor. The canonical supplies per-unit voltage-drop formulas and sensitivity branches (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** Starting power factor is given as zero, but the motor’s rated kVA, efficiency, and rated operating power factor needed to derive the rated-current base are absent.
- **Blocker / precise next step:** `missing_parameter`. Supply the motor rated kVA or equivalent rated power factor and efficiency, then recompute both sides’ voltage variation with the evidenced starting condition.
- **Recommended classification:** retain `needs_manual_review`; `conditional_numeric`.

### EE-111-06-3 — Industrial distribution, 111 Q3

- **Current status:** `needs_manual_review`; disposition `motor_rating_branches`; chapter: cogeneration system and three-phase subtransient fault analysis (`dashboard-data.js:L2039`, `dashboard-data.js:L6312`, `dashboard-data.js:L8622-L8632`; `data/pe-solution-audit.json:L1230-L1243`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_工業配電.pdf`, SHA-256 `53a7db6996da137566fc7ef09444b0d9626812b7dd47c9c7ddfa9174be507feb`; crop `PE_111年_工業配電_Q03.png`, file page 2, rectangle `[0,205.87,595.22,568.07]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4541-L4589`). The crop fixes the three motor branches, F/A locations, the generator’s 25 MW and 22.8 kV, transformer, and motor/generator reactance data. The canonical provides conditional 25 MVA-base / `E''=1 pu` branches and an explicit generator-side expression (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** Branch count and topology are verified, but the generator rated MVA/PF, motor rated apparent power or equivalent PF/efficiency, and pre-fault internal emfs are not all supplied, so neither requested current is uniquely fixed.
- **Blocker / precise next step:** `missing_parameter`. Confirm the generator rating convention and pre-fault internal-emf assumptions; obtain each motor’s rated apparent power or PF/efficiency and the required pre-fault emfs; only then lock F and A currents.
- **Recommended classification:** retain `needs_manual_review`; `motor_rating_branches`.

### EE-111-06-4 — Industrial distribution, 111 Q4

- **Current status:** `needs_manual_review`; disposition `code_compliance_branches`; chapter: motor wiring, conductor ampacity, and overcurrent protection (`dashboard-data.js:L2060`, `dashboard-data.js:L6314`, `dashboard-data.js:L8587-L8593`; `data/pe-solution-audit.json:L1244-L1257`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_工業配電.pdf`, SHA-256 `53a7db6996da137566fc7ef09444b0d9626812b7dd47c9c7ddfa9174be507feb`; crop `PE_111年_工業配電_Q04.png`, file page 2, rectangle `[0,576.07,595.22,824]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4541-L4608`). The crop contains the complete question but no motor nameplate or ampacity table. The canonical documents the historical-table cross-check: 20 HP=54 A, 10 HP=28 A, 7.5 HP=22 A, while 8 HP is not listed, and records the dependency on material, conductor count, correction factor, and regulation version (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** The wiring task cannot be uniquely sized because the 8 HP full-load current and applicable historical ampacity/conductor-installation conditions are absent.
- **Blocker / precise next step:** `missing_parameter`. Inspect the official original page/crop, establish the 111-year regulation/table version, provide the 8 HP full-load current, conductor material, number of current-carrying conductors, and correction factors, then select conductor and protection ratings.
- **Recommended classification:** retain `needs_manual_review`; `code_compliance_branches`.

### EE-106-02-2 — Electronics, 106 Q2

- **Current status:** `needs_manual_review`; disposition `parameterized_only`; chapter: MOSFET differential amplifier and negative feedback (`dashboard-data.js:L4249`, `dashboard-data.js:L6052`, `dashboard-data.js:L8522-L8528`; `data/pe-solution-audit.json:L2658-L2671`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/106年/106年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `1f266a94ab731b9335d992b28a7e8e987891308fc53ff51dd5880949eda0a06e`; crop `PE_106年_電子學（包括電力電子學）_Q02.png`, file pages 1–2, rectangles `[0,546.92,729,1014]` and `[0,18,729,164.45]`, `pdf_text_sequence` / `text_sequence` (`CROP:L1739-L1768`). The crop fixes the differential/rebating topology and asks that all MOSFET `r_o` be considered. The canonical retains the feedback formula and test-source definition but records the absent device and resistor parameters (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** Topology and a symbolic feedback relation are available; numerical closed-loop gain and output resistance are not unique without `R1`, `R2`, each device’s `g_m/r_o`, tail-source small-signal impedance, and the precise output port.
- **Blocker / precise next step:** `missing_parameter`. Obtain those component/device values and output-port definition from an authoritative source, then evaluate the parameterized closed-loop quantities.
- **Recommended classification:** retain `needs_manual_review`; `parameterized_only`.

### EE-109-02-3 — Electronics, 109 Q3

- **Current status:** `needs_manual_review`; disposition `conduction_mode_branches`; chapter: flyback converter CCM/DCM current and efficiency (`dashboard-data.js:L2723`, `dashboard-data.js:L6228`, `dashboard-data.js:L8496-L8502`; `data/pe-solution-audit.json:L1678-L1691`; `CAN:L2-L16`).
- **Available source evidence:** official PDF `依年度分類/109年/109年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `a06179b3e8dceea246eae69d1df7e7e0c41a72856c0f2468bbba9ffe63a85b93`; crop `PE_109年_電子學（包括電力電子學）_Q03.png`, file page 2, rectangle `[0,75,595.22,437]`, `manual_audit` / `audited` (`CROP:L3644-L3701`). The crop fixes turns ratio, output voltage, duty, frequency, and the flyback topology. The canonical’s DCM back-substitution gives `I_p,max=60 A` and demagnetization time equal to the off-time, placing the chosen calculation at DCM/critical boundary (`CAN:L13-L15` and the warning at `CAN:L20-L20`).
- **Uniquely verifiable:** **No.** The flyback topology is established, but the official evidence does not specify CCM versus DCM or the initial magnetizing-current condition; CCM and DCM definitions/results therefore remain different branches.
- **Blocker / precise next step:** `missing_parameter`. Confirm the intended conduction mode and current definitions (average, peak, primary/secondary, and initial magnetizing current) from the authoritative question context before choosing one branch.
- **Recommended classification:** retain `needs_manual_review`; `conduction_mode_branches`.

### EE-111-02-3 — Electronics, 111 Q3

- **Current status:** `needs_manual_review`; disposition `inconsistent_data_branches`; chapter: MOSFET common-source source degeneration and bias design (`dashboard-data.js:L1692`, `dashboard-data.js:L6342`, `dashboard-data.js:L8503-L8509`; `data/pe-solution-audit.json:L1048-L1061`; `CAN:L2-L16`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `456244f96e6ff70b2e477177ee582234ae115e047624bd7927a326f42d5be858`; crop `PE_111年_電子學（包括電力電子學）_Q03.png`, file page 2, rectangle `[0,60.3,595.22,319.18]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4856-L4904`). The crop simultaneously gives `|A_v|=5`, `I_DS=3.17 mA`, `R_S=30 Ω`, `R_D=200 Ω`, `μ_nC_ox`, and `V_S=V_OV`. Independent rechecking obtains `g_m=0.100 S` from the gain but `0.0666667 S` from square law; the canonical preserves both branches and the minimal `R_S=26.666667 Ω` repair if gain 5 is retained (`CAN:L12-L15`).
- **Uniquely verifiable:** **No.** The conflict is in the supplied numerical data, not merely an unstated modeling convention.
- **Blocker / precise next step:** `source_conflict`. Confirm whether the official value `|A_v|=5` or `R_S=30 Ω` is erroneous/corrected. Keep the official `3.17 mA` and the square-law branch separate until that conflict is resolved.
- **Recommended classification:** retain `needs_manual_review`; `inconsistent_data_branches`.

### EE-111-02-4 — Electronics, 111 Q4

- **Current status:** `needs_manual_review`; disposition `parameterized_only`; chapter: shunt-series current-feedback amplifier and BJT small-signal model (`dashboard-data.js:L1708`, `dashboard-data.js:L6344`, `dashboard-data.js:L8541-L8547`; `data/pe-solution-audit.json:L1062-L1075`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `456244f96e6ff70b2e477177ee582234ae115e047624bd7927a326f42d5be858`; crop `PE_111年_電子學（包括電力電子學）_Q04.png`, file page 2, rectangle `[0,327.18,595.22,824]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4856-L4923`). The crop fixes the Q1/Q2, `R_F`, and `R_L` topology and `V_A=∞`, but does not label the numerical `R_C`, `R_F`, `R_L`, `g_m`, `r_π`, or `β`. The canonical records the current-current feedback topology, KCL definitions, and test-source formulas (`CAN:L12-L14`).
- **Uniquely verifiable:** **No.** The feedback topology and symbolic setup are available; none of the five requested numerical quantities is uniquely determined from the supplied values.
- **Blocker / precise next step:** `missing_parameter`. Obtain `R_C`, `R_F`, `R_L`, `g_m`, `r_π`/`β`, and an unambiguous open-circuit output-port definition, then numerically evaluate the five quantities.
- **Recommended classification:** retain `needs_manual_review`; `parameterized_only`.

### EE-112-02-1 — Electronics, 112 Q1

- **Current status:** `needs_manual_review`; disposition `conditional_numeric`; chapter: BJT common-base amplifier and high-frequency response (`dashboard-data.js:L1162`, `dashboard-data.js:L6394`, `dashboard-data.js:L8529-L8540`; `data/pe-solution-audit.json:L712-L725`; `CAN:L2-L18`).
- **Available source evidence:** official PDF `依年度分類/112年/112年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `60e5db5eb1f1b348f80c276a01299d13a12b2f201ac7c5bb80c0768ffcf31509`; crop `PE_112年_電子學（包括電力電子學）_Q01.png`, file page 1, rectangle `[0,234.91,595.22,484.18]`, `pdf_text_sequence` / `text_sequence` (`CROP:L5448-L5458`). The crop fixes `β=100`, `I_Q=0.5 mA`, the capacitors, resistors, and common-base topology. Canonical KCL resolves the current-source relation as `I_Q=I_C+I_B=I_E`, but the high-frequency and gain numerical branches retain `V_T=25/25.85/26 mV` (`CAN:L12-L17`).
- **Uniquely verifiable:** **No for the full numerical answer.** The topology and current relation are supported; `V_T` or junction temperature is not specified, so the requested high-frequency poles and gain are not unique.
- **Blocker / precise next step:** `missing_parameter`. Confirm the intended `V_T` or junction temperature. Keep the finite-β KCL branch and do not replace `I_E` with `I_C` without evidence.
- **Recommended classification:** retain `needs_manual_review`; `conditional_numeric`.

### EE-113-02-2 — Electronics, 113 Q2

- **Current status:** `needs_manual_review`; disposition `conditional_numeric`; chapter: BJT common-base amplifier and T model (`dashboard-data.js:L666`, `dashboard-data.js:L6452`, `dashboard-data.js:L8510-L8521`; `data/pe-solution-audit.json:L418-L431`; `CAN:L2-L18`).
- **Available source evidence:** official PDF `依年度分類/113年/113年_電機工程技師_電子學（包括電力電子學）.pdf`, SHA-256 `d375cf693e067761ddd2cd62645b5fd01decf8b31fee88517c10581e6bc96270`; crop `PE_113年_電子學（包括電力電子學）_Q02.png`, file page 1, rectangle `[0,486.89,595.22,824]`, `pdf_text_sequence` / `text_sequence` (`CROP:L6049-L6078`). The crop fixes `α=0.99`, `I_E=0.5 mA`, `R_sig=75 Ω`, `R_C=R_L=12 kΩ`, and the AC-grounded base. The canonical’s T-model calculation gives different gain branches for `V_T=25` and `25.85 mV`, and records 26 mV as another retained branch (`CAN:L12-L17`).
- **Uniquely verifiable:** **No.** The T-model topology and resistor/current data are available, but `V_T`/temperature is missing, so `R_in` and voltage gain cannot be declared unique.
- **Blocker / precise next step:** `missing_parameter`. Confirm the problem’s intended thermal voltage or junction temperature; retain the 25/25.85/26 mV branches until then.
- **Recommended classification:** retain `needs_manual_review`; `conditional_numeric`.

### EE-105-04-5 — Electrical machinery, 105 Q5

- **Current status:** `needs_manual_review`; disposition `flux_curve_parameterized`; chapter: DC-machine characteristics and speed control (`dashboard-data.js:L5102`, `dashboard-data.js:L6004`, `dashboard-data.js:L8548-L8554`; `data/pe-solution-audit.json:L3106-L3119`; `CAN:L2-L17`).
- **Available source evidence:** official PDF `依年度分類/105年/105年_電機工程技師_電機機械.pdf`, SHA-256 `2847ecad4360ee2ba88a6935845e092b2d2b3361c60bcb401ce03465c3adc269`; crop `PE_105年_電機機械_Q05.png`, file page 1, rectangle `[0,692.22,729,1014]`, `pdf_text_sequence` / `text_sequence` (`CROP:L1149-L1235`). The crop fixes rated voltage, armature resistance/current, field-current change `12→6 A`, base speed, and half-rated torque. Canonical back-substitution fixes the armature-emf terms but states that the speed `1200 rpm` requires the extra linear unsaturated assumption `Φ_2/Φ_1=0.5` (`CAN:L13-L16`, `CAN:L21-L22`).
- **Uniquely verifiable:** **No for speed.** The magnetic-circuit relation is not fixed by field current alone without a magnetization curve or an explicit unsaturated assumption.
- **Blocker / precise next step:** `missing_parameter`. Supply the magnetization curve or authoritative statement that the machine is unsaturated/linear; only then select the flux ratio and speed.
- **Recommended classification:** retain `needs_manual_review`; `flux_curve_parameterized`.

### EE-111-04-4 — Electrical machinery, 111 Q4

- **Current status:** `needs_manual_review`; disposition `curve_interpolation_branches`; chapter: synchronous-generator equivalent circuit and short-circuit ratio (`dashboard-data.js:L1879`, `dashboard-data.js:L6352`, `dashboard-data.js:L8555-L8561`; `data/pe-solution-audit.json:L1118-L1131`; `CAN:L2-L15`).
- **Available source evidence:** official PDF `依年度分類/111年/111年_電機工程技師_電機機械.pdf`, SHA-256 `81d4c8635b29f70234ca5d74ab2ac5d21480f4a3cea94c07ac67b80c06d2f3e8`; crop `PE_111年_電機機械_Q04.png`, file page 3, rectangle `[0,29.51,595.22,333.71]`, `pdf_text_sequence` / `text_sequence` (`CROP:L4942-L5009`). The crop fixes the rated voltage/current, power factor, and synchronous reactance. Canonical independently verifies part (1) as 68.6414%, but records that the official page contains no OCC/SCC curve, axes, or interpolation points for parts (2) and (3) (`CAN:L12-L14`, `CAN:L19-L21`).
- **Uniquely verifiable:** **Only partially.** Part (1) is uniquely verifiable from the supplied phasor data; parts (2) and (3) are not, because their requested curve readings are absent.
- **Blocker / precise next step:** `graph_estimate`. Locate the actual OCC/SCC curves or an official linear-interpolation rule. Until then retain the two curve-derived values only as explicitly labeled linear-proportion conditions.
- **Recommended classification:** retain `needs_manual_review`; `curve_interpolation_branches`.

### EE-113-04-4 — Electrical machinery, 113 Q4

- **Current status:** `needs_manual_review`; disposition `source_conflict_branches`; chapter: three-phase induction-motor equivalent circuit and torque (`dashboard-data.js:L868`, `dashboard-data.js:L6464`, `dashboard-data.js:L8562-L8568`; `data/pe-solution-audit.json:L502-L515`; `CAN:L2-L16`).
- **Available source evidence:** official PDF `依年度分類/113年/113年_電機工程技師_電機機械.pdf`, SHA-256 `25589a797748fa245573451ff209e8242c1181a9416604a7de58b7e3487c26c9`; crop `PE_113年_電機機械_Q04.png`, file page 2, rectangle `[0,60,595.22,392]`, `manual_audit` / `audited` (`CROP:L6135-L6202`). The crop fixes 220 V, 60 Hz, 1120 rpm, `Z_1`, the depicted `Z_2=0.2/s+j0.35 Ω`, `R_c`, and `X_m`; the canonical also records official question text containing the mechanical-load expression `0.1(1-s)/s`, which conflicts with the depicted `0.2/s` branch (`CAN:L13-L15`, `CAN:L18-L22`).
- **Uniquely verifiable:** **No.** Two mutually inconsistent values are present in the official evidence; the resulting current, torque, efficiency, and maximum-torque calculations depend on which interpretation is selected.
- **Blocker / precise next step:** `source_conflict`. Obtain an official correction or human ruling identifying whether the diagram’s `0.2/s` or the prompt’s `0.1(1-s)/s` is the intended mechanical-load basis. Keep both recalculation branches separate.
- **Recommended classification:** retain `needs_manual_review`; `source_conflict_branches`.

## Final disposition

No question is recommended for upgrade. The local evidence supports dedicated canonical records and reproducible conditional work for all 17, but the blockers remain material: 12 `missing_parameter` cases, 1 `official_wording_ambiguity` case, 2 `graph_estimate` cases, and 2 `source_conflict` cases. The appropriate next action is human acquisition or adjudication of the exact missing source condition identified above, followed by an independent recheck; until that happens, the audit status should remain `needs_manual_review`.
