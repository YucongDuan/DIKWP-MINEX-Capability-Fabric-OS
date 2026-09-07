# MINEX-1000:2026-DRAFT

## Minimum Verified Execution Expenditure Capability Protocol
## 最小可验证执行耗费能力协议

**Status / 状态:** Author-side pre-standard draft / 作者侧预标准草案  
**Version / 版本:** 1.0.0  
**Date / 日期:** 2026-09-07

---

## 1. Scope / 范围

MINEX-1000 specifies machine-readable intents, capability manifests, route construction, authority and quality gates, multidimensional execution expenditure, Pareto selection, result receipts, bounded capability leases, proposal-only markets, recipe distillation, successor reauthorization, and conformance claims.

MINEX-1000规定机器可读意图、能力清单、路线构建、权限和质量硬门、多维执行耗费、Pareto选择、结果收据、有界能力租约、提案型市场、配方蒸馏、后继重授权和符合性声明。

It does not grant legal authority, define payment regulation, certify physical energy measurements, or authorize unrestricted remote execution.

本规范不授予法律权限，不规定支付监管制度，不认证物理能耗测量，也不授权无限制远程执行。

## 2. Normative terms / 规范词

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as normative requirement levels.

“必须”“不得”“应”“不应”“建议”“可以”“可选”表示相应规范强度。

## 3. Core objects / 核心对象

### 3.1 Intent

An Intent MUST contain:

- stable `intent_id`;
- human-readable title and purpose;
- available semantic input types;
- required output types;
- explicitly granted authority scopes;
- hard constraints;
- disclosed route-selection weights;
- owner realm and currency context.

### 3.2 Capability Manifest

A capability MUST contain:

- stable identifier and name;
- provider and owner realm;
- execution surface;
- required and provided semantic types;
- quality estimate;
- authority scopes;
- side-effect class;
- cost vector and measurement source;
- executor or proposal metadata;
- provenance and terms.

### 3.3 Route

A route is an ordered sequence of capabilities whose outputs satisfy subsequent input requirements and whose final semantic types satisfy the intent.

路线是一个有序能力序列，其前序输出必须满足后序输入，最终语义类型必须满足意图。

### 3.4 Receipt

A receipt binds intent, plan, selected route, execution outcome, limitations, and digests. A valid receipt does not prove universal correctness.

## 4. Execution surfaces / 执行表面

Conforming implementations MUST distinguish at least:

```text
model_native
local_code
local_api
local_gui
same_owner_peer
market_service
human_delegate
recipe
```

An implementation MUST NOT infer authority from surface accessibility.

## 5. Cost vector / 耗费向量

Implementations MUST preserve at least:

```text
expected_energy_j
latency_ms
money
human_minutes
data_exposure
carbon_g
semantic_loss
failure_probability
```

Values with different units MUST NOT be summed before disclosure and normalization. Each value MUST carry a measurement-source class.

Expected energy SHOULD include execution, verification, coordination, and expected retry energy.

## 6. Admissibility / 有效性

A route MUST be rejected when:

- a required authority scope is absent;
- a surface is disallowed;
- a network or purchase path lacks explicit permission;
- the side-effect class exceeds the intent limit;
- a hard budget is exceeded;
- route quality falls below the minimum;
- a same-owner peer belongs to a different owner realm;
- a capability is unavailable.

A rejected route MUST retain reason codes.

## 7. Optimization / 优化

Implementations SHALL compute or approximate a Pareto frontier over admissible routes. A route A dominates route B only if A is no worse in every declared cost dimension and quality, and strictly better in at least one.

A weighted score MAY be used only after hard gates and Pareto filtering. References and weights MUST be disclosed.

## 8. Execution / 执行

Reference local execution MUST use an allowlist of handlers. Arbitrary shell execution MUST NOT be enabled by default.

External API, GUI, peer, market, or human routes MAY remain proposal-only. A proposal MUST NOT be reported as executed.

## 9. Capability leases / 能力租约

A lease MUST bind:

- capability identifier;
- provider and consumer;
- owner realm;
- issue and expiry time;
- call budget;
- request nonce and replay control;
- monetary budget;
- signature or equivalent integrity evidence;
- external-action authority.

A lease MUST NOT imply general access to a provider node. Expired, exhausted, revoked, or invalid leases MUST be rejected.

## 10. Market exchange / 市场交换

A market bid SHOULD expose price, currency, quality, expected expenditure, output types, availability, and warranty terms.

Settlement MUST bind to a result receipt. The reference implementation MUST keep automatic payment authority at zero.

## 11. Recipe distillation / 配方蒸馏

Only a verified completed route MAY be distilled. A recipe MUST retain source-receipt provenance and MUST NOT add authority.

Recipe recursion MUST fail closed. Each expanded capability MUST remain registered and independently governed.

## 12. Successor agents / 后继Agent

Authority MUST NOT be inherited solely from predecessor artifacts, memory, caches, prompts, or recipes. A successor MUST obtain a fresh lease or mandate.

Stop and revocation procedures SHOULD cover tasks, leases, credentials, caches, scheduled work, and successor manifests.

## 13. Energy and carbon claims / 能耗与碳声明

An implementation claiming physical measurement MUST disclose hardware, boundary, functional unit, method, repetitions, software version, and uncertainty where available.

Provider-reported or modeled values MUST NOT be labeled as independently measured.

## 14. Appeals and correction / 申诉与纠错

A consequential adverse route decision SHOULD provide reason codes, scope, expiry, and correction procedure. Incorrect records MUST be superseded rather than silently rewritten.

## 15. Interoperability / 互操作

Implementations MAY expose:

- JSON Schema 2020-12;
- MCP tool descriptions;
- A2A Agent Cards, Tasks, and Artifacts;
- OpenAPI descriptions;
- software-carbon or energy measurement extensions.

Interoperability output MUST NOT be represented as third-party certification.

## 16. Conformance levels / 符合等级

| Level | English | 中文 |
|---|---|---|
| L0 | Intent and semantic outcome | 意图与语义结果 |
| L1 | Capability manifests and surfaces | 能力清单与执行表面 |
| L2 | Authority, quality, privacy, budget, and side-effect gates | 权限、质量、隐私、预算与副作用硬门 |
| L3 | Pareto routing, declared weights, and result receipts | Pareto路线、公开权重与结果收据 |
| L4 | Leases, proposal market, recipes, and successor reauthorization | 租约、提案市场、配方与后继重授权 |
| L5 | Production identity, revocation, measurement, settlement, and independent assessment | 生产身份、撤销、测量、结算与独立评估 |

A claim at level Ln MUST satisfy every lower level.

## 17. Minimum requirement catalogue / 最低规范条款

The following identifiers are normative:

```text
M100 intent identifier
M101 purpose and semantic input/output
M102 owner realm and currency
M103 disclosed constraints
M104 disclosed weights
M110 capability identifier
M111 provider and owner realm
M112 execution surface
M113 semantic requires/provides
M114 quality
M115 authority scopes
M116 side effect
M117 cost vector
M118 measurement source
M119 provenance and terms
M200 no authority from interface access
M201 missing scope rejects route
M202 network requires explicit permission
M203 purchase requires explicit permission
M204 peer owner realm must match
M205 side-effect limit
M206 hard budgets
M207 minimum quality
M208 rejection reason codes
M209 unavailable capability excluded
M300 preserve separate cost units
M301 retry-adjusted energy
M302 Pareto analysis
M303 weighted score after gates
M304 disclose references and weights
M305 no cheapness override
M400 allowlisted local handlers
M401 no unrestricted shell by default
M402 proposal not reported as execution
M403 execution outcome digest
M404 limitations in receipt
M405 append-only responsibility record
M500 lease capability binding
M501 lease provider/consumer binding
M502 lease expiry
M503 lease call budget
M504 lease money budget
M505 lease integrity evidence
M506 no general node authority
M507 lease validation and rejection reasons
M510 market typed output
M511 market budget gate
M512 result-bound settlement proposal
M513 automatic payment authority zero
M520 verified-route recipe only
M521 recipe provenance
M522 recipe no authority expansion
M523 recipe recursion rejection
M524 registered expanded steps
M530 successor fresh authority
M531 stop and revocation propagation
M600 measurement classification
M601 physical measurement disclosure
M602 modeled values not mislabeled
M610 correction preserves history
M620 machine-readable schema
M621 MCP reference mapping
M622 A2A reference mapping
M623 OpenAPI reference mapping
M624 no false certification claim
M700 external action authority zero in reference core
M701 automatic contract authority zero
M702 automatic remote publication authority zero
M703 adverse evidence retained
M704 documented reality boundary
```
