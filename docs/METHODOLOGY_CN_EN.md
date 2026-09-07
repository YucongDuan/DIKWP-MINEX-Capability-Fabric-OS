# MINEX Methodology / MINEX 方法论

## 1. Functional unit / 功能单位

Every comparison MUST use the same semantic outcome and acceptance criteria. Comparing “one API call” with “one GUI click” is invalid if the resulting functionality differs.

所有比较必须采用相同的语义结果和验收条件。若最终功能不同，则“一次API调用”和“一次GUI点击”不可直接比较。

## 2. Cost vector / 耗费向量

\[
\mathbf C=(E,T,M,H,X,G,L,P_f)
\]

- `expected_energy_j`: execution, verification, coordination, and expected retry energy;
- `latency_ms`: end-to-end elapsed time;
- `money`: user-declared currency cost;
- `human_minutes`: required human attention, not total wall-clock time;
- `data_exposure`: probability-like exposure index in [0,1];
- `carbon_g`: declared or measured grams CO2e for the functional unit;
- `semantic_loss`: loss of relevant meaning or constraints in [0,1];
- `failure_probability`: estimated probability that the route fails acceptance.

## 3. Expected energy / 预期能耗

\[
E_{exp}=E_{exec}+E_{verify}+E_{coord}+\frac{p_f}{1-p_f}E_{retry}
\]

The geometric retry term assumes independent repeated attempts. Domains with correlated failures SHOULD replace it with an empirical model.

几何重试项假定各次尝试独立；若失败高度相关，应使用经验模型替换。

## 4. Route quality / 路线质量

Reference heuristic:

\[
Q(\rho)=\min_j q_j(1-L)(1-0.35P_f)
\]

This is not a psychometric or universal scientific scale. Implementations SHOULD calibrate it against domain acceptance results.

## 5. Hard gates / 硬门

A route is inadmissible when any capability:

- requires a scope not granted by the intent;
- uses a disallowed surface;
- exceeds the maximum side effect;
- exceeds energy, time, money, attention, privacy, carbon, semantic-loss, or failure budgets;
- falls below minimum route quality;
- uses a network or purchase path when not explicitly allowed.

## 6. Pareto dominance / Pareto支配

Route A dominates route B if A is no worse in every cost dimension, no worse in quality, and strictly better in at least one dimension.

## 7. Normalized selection / 归一化选择

For Pareto routes only:

\[
J=\sum_kw_k\frac{c_k/r_k}{1+c_k/r_k}
\]

Reference values \(r_k\) and weights \(w_k\) MUST be disclosed.

## 8. Measurement confidence / 测量置信

Cost values SHOULD carry one of:

```text
measured
provider-reported
benchmark-derived
declared
not-physically-measured
```

Measured values SHOULD include hardware, runtime, boundary, functional unit, repetition count, and uncertainty.

## 9. Distillation / 配方蒸馏

Only a verified completed local reversible route may be distilled. A recipe MUST retain its source-receipt digest and step identifiers. Distillation MUST NOT add authority.

只有已验证、本地完成且可逆的路线可以蒸馏。配方必须保留来源收据摘要和步骤标识，且不得增加权限。

## 10. Calibration loop / 校准闭环

```text
plan
→ execute
→ measure
→ verify outcome
→ compare prediction with reality
→ update cost and quality estimates
→ retire invalid recipe or capability
```
