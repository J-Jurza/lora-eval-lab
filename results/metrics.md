# Metrics

Pairs judged 194, kept after swap consistency 171, dropped {'inconsistent across swap': 23}.

| Outcome | Rate | 95% CI |
|---|---|---|
| Tuned preferred | 0.339 | 0.269 to 0.409 |
| Base preferred | 0.515 | |
| Tie | 0.146 | |

Sensitivity, dropped pairs counted as ties: tuned 0.299, base 0.454, tie 0.247.

| Dimension | Base | Tuned | Diff | 95% CI |
|---|---|---|---|---|
| faithfulness | 4.42 | 4.05 | -0.37 | -0.63 to -0.11 |
| completeness | 4.25 | 4.01 | -0.23 | -0.45 to -0.00 |
| format | 4.51 | 4.42 | -0.09 | -0.29 to +0.11 |
| concision | 4.45 | 4.37 | -0.08 | -0.27 to +0.11 |

| Section | n | Tuned | Base | Tie |
|---|---|---|---|---|
| History of Present Illness | 44 | 0.41 | 0.55 | 0.05 |
| Family and Social History | 38 | 0.37 | 0.53 | 0.11 |
| Review of Systems | 16 | 0.19 | 0.75 | 0.06 |
| Past Medical History | 13 | 0.69 | 0.15 | 0.15 |
| Assessment | 11 | 0.45 | 0.55 | 0.00 |
| Allergies | 10 | 0.10 | 0.30 | 0.60 |
| Medications | 9 | 0.22 | 0.33 | 0.44 |
| Chief Complaint | 7 | 0.29 | 0.71 | 0.00 |
| Past Surgical History | 6 | 0.17 | 0.17 | 0.67 |
| Physical Examination | 4 | 0.50 | 0.50 | 0.00 |
| Emergency Department Course | 4 | 0.00 | 0.75 | 0.25 |
| Other History | 2 | 0.00 | 1.00 | 0.00 |
| Plan | 1 | 0.00 | 1.00 | 0.00 |
| Disposition | 1 | 0.00 | 1.00 | 0.00 |
| Laboratory Results | 1 | 0.00 | 1.00 | 0.00 |
| Procedures | 1 | 1.00 | 0.00 | 0.00 |
| Gynaecological History | 1 | 0.00 | 1.00 | 0.00 |
| Diagnosis | 1 | 0.00 | 0.00 | 1.00 |
| Imaging | 1 | 0.00 | 1.00 | 0.00 |

ROUGE-L F1 against the reference: base 0.183, tuned 0.282. ROUGE rewards overlap, not correctness.

Human vs judge on 29 kept pairs: raw agreement 0.69, Cohen's kappa 0.41.

Failure taxonomy over losses (88/88 labelled):

| Failure | Count |
|---|---|
| hallucinated fact | 41 |
| omitted fact | 35 |
| wrong section | 1 |
| format break | 6 |
| other | 5 |
