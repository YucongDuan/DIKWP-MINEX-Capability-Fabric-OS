# DIKWP MINEX Capability Fabric OS v1.0.0

## Intent-to-Outcome Infrastructure for Model-First Computing

**Release date:** 7 September 2026  
**Pre-standard:** MINEX-1000:2026-DRAFT  
**Operating mode:** MESH95_INTENT_CAPABILITY_PARETO_MINIMUM_EXPENDITURE_LEASE_RECEIPT_CLOSURE

---

## Executive summary

Frontier models increasingly unify reasoning, generated code, formal APIs, browsers, professional applications, direct computer use, and long-running tool loops. A user can state an outcome while an agent decides whether to reason directly, generate a deterministic program, invoke an API, operate a GUI, borrow a capability from another computer, purchase a service, or request human review.

This does not make applications, APIs, or authorization obsolete. Applications remain valuable as systems of record, identity and policy boundaries, specialist runtimes, auditable executors, and durable stores. What changes is the assumption that the application must own navigation and workflow order.

DIKWP MINEX provides the missing control layer. It represents each function as a machine-readable capability with semantic inputs and outputs, quality, authority, expenditure, provenance, reversibility, and execution surface. It represents the desired outcome as a constrained intent. It composes candidate routes, rejects invalid ones, computes a Pareto frontier, and selects the lowest declared **minimum verified execution expenditure** route.

The system addresses five structural problems:

1. when the model should perform a function directly and when software should execute it;
2. how code, API, and GUI paths should compete on measured or declared cost and reliability;
3. how one owner can borrow narrowly scoped capabilities across computers;
4. how independent parties can trade capability results with receipt-bound settlement proposals;
5. how successful routes can become reusable procedural recipes without inheriting hidden authority.

MINEX does not reduce “energy” to electricity alone. It preserves physical energy, latency, money, human attention, data exposure, carbon, semantic loss, and failure probability as separate dimensions. Authority, quality, privacy, and reversibility remain hard gates.

---

## 1. Source discrimination: an interface wall, not a permission wall

The supplied background article argues that computer use is becoming a normal execution surface; agents can choose among APIs, browsers, shells, code, and GUIs during a task; and graphical interfaces increasingly act as machine interfaces. It also correctly distinguishes the interface wall from identity, permission, policy, and data walls. The article itself notes that its author had not independently tested the new model at the time of writing.

Official OpenAI material provides narrower support. GPT-6 Astra is presented as materially stronger in computer use and professional workflows. OpenAI's computer-use documentation lists generated code, structured computer actions, and existing function or remote MCP interfaces as alternative integration paths, recommends code execution for Astra, and requires an isolated environment with permission and execution limits.

MINEX therefore fixes three invariants:

\[
GUIAccess\neq Authorization
\]

\[
ModelCapability\neq BusinessAuthority
\]

\[
ApplicationOptionality\neq ApplicationIrrelevance
\]

The model gains route choice, not legal or technical ownership of the systems it can see.

---

## 2. From application economics to capability economics

The application-centric pattern is:

```text
user knows goal
→ user chooses application
→ user adapts to its interface
→ application defines order
→ result remains inside the application
```

The model-first pattern is:

```text
user declares purpose
→ system identifies semantic result
→ capabilities are discovered
→ model, code, API, GUI, peer, market, and human paths compete
→ an admissible low-expenditure route is selected
→ the result is committed to an appropriate system of record
```

A capability is defined as:

\[
Capability=
(
InputSemantics,
OutputSemantics,
Quality,
Authority,
Cost,
Surface,
Provenance,
Terms
)
\]

This creates surface liquidity, spatial liquidity, and economic liquidity without pretending that implementation, authorization, or data ownership are interchangeable.

---

## 3. DIKWP semantic routing

MINEX routes semantic types rather than application screens. Examples include:

```text
text.raw
text.summary
text.stats
json.normalized
table.profile
report.markdown
artifact.sha256
```

An intent is:

\[
I=(P,X,Y,Q,A,B,W)
\]

where purpose, available inputs, required results, quality constraints, granted authority, budgets, and preference weights are explicit.

DIKWP is implemented as a graph of transformations rather than a mandatory one-way pipeline. Data can become information; information can be tested into knowledge; knowledge can be contextualized into wisdom; wisdom can define actionable purpose; and the outcome can return as new data and evidence.

---

## 4. Eight execution surfaces

### Model-native

Useful for synthesis, explanation, drafting, and open-ended reasoning. Its costs may include provider fees, privacy exposure, verification effort, semantic drift, and retries.

### Local code

Useful for deterministic transformations, batch processing, validation, hashing, statistics, and structured data. It is repeatable and can be kept local.

### Local or formal API

A fast, stable, measurable, and permission-aware path. Computer use does not eliminate the advantages of a formal interface.

### Local GUI / computer use

A fallback or specialist path when no suitable formal interface exists. MINEX explicitly includes visual loops, popups, state drift, verification, and retries in its expected cost.

### Same-owner peer

A device can borrow a specific capability from another authorized device without gaining general remote control. The call requires a bounded lease.

### Market service

An external provider can offer a typed result with price, expected expenditure, quality, provenance, and warranty terms. The reference core performs proposal-only clearing.

### Human delegate

Human judgment remains a legitimate capability for negotiation, law, medicine, ethics, relationship context, and consequential approval.

### Verified recipe

A completed local route can be compressed into a registered recipe carrying typed steps, provenance, quality, and authority boundaries.

---

## 5. Minimum verified execution expenditure

A route retains a vector:

\[
\mathbf C(\rho)=
(E,T,M,H,X,G,L,P_f)
\]

covering expected physical energy, latency, money, human attention, data exposure, carbon, semantic loss, and failure probability.

Expected energy includes verification, coordination, and expected rework:

\[
E_{exp}
=
E_{exec}+E_{verify}+E_{coord}
+
\frac{p_f}{1-p_f}E_{retry}
\]

A route that appears cheap per attempt can be expensive after retries and human supervision.

Admissibility is evaluated before optimization:

\[
\mathcal R^*=
\{\rho\mid Authority,Quality,Privacy,Budget,Reversibility\}
\]

The Pareto frontier is:

\[
PF=\{\rho\in\mathcal R^*: \nexists\rho'\prec\rho\}
\]

Only within that frontier is a transparent normalized score used:

\[
J(\rho)=
\sum_k w_k
\frac{c_k/r_k}{1+c_k/r_k}
\]

No amount of low cost can compensate for missing authorization.

---

## 6. A strict meaning of capability internalization

Tool fluency does not by itself prove that a model has permanently absorbed an API into its weights. MINEX separates:

| Level | Meaning |
|---|---|
| I0 | re-plan from scratch |
| I1 | retain capability descriptions |
| I2 | distill a verified route into a replayable recipe |
| I3 | recalibrate the recipe from repeated measurements |
| I4 | explicitly train or modify model parameters and independently evaluate the change |

The reference implementation reaches I2. A recipe is:

\[
K_{recipe}=Compress(Trace,Types,Authority,Receipt)
\]

It reduces planning and coordination overhead but cannot copy proprietary implementations or inherit implicit rights.

---

## 7. Cross-device capability borrowing

A capability lease binds:

\[
L=(C,P,R,O,T,N,B,S)
\]

representing capability, provider, consumer, owner realm, expiry, call budget, money budget, and signature.

Ownership of both devices does not remove compartment boundaries. A home device, work computer, cloud node, and health-data device may require different scopes and disclosure policies.

A successor agent does not inherit a predecessor's lease:

\[
SuccessorAuthority
\not\Leftarrow
PredecessorArtifact
\]

This is important because the supplied multi-agent background describes methods and artifacts that can propagate across agents and generations even after individual instances stop.

---

## 8. Capability exchange

A bid includes provider, capability, output type, price, currency, expected energy, quality, availability, owner-realm restrictions, and warranty terms.

A valid settlement must bind a winning bid to a verified result receipt and dispute terms. The reference implementation always returns:

```text
PROPOSAL_ONLY_NO_REAL_PAYMENT
```

It has no bank, wallet, contract, tax, or asset-transfer authority.

A mature capability exchange could allow models, software vendors, personal devices, organizations, and human experts to compete as capability suppliers. It must not become a hidden-ranking market that sells user data, silently outsources sensitive tasks, or leaves failed results without correction.

---

## 9. Energy and carbon evidence

MINEX distinguishes:

```text
measured
provider-reported
declared or modeled
```

A physical measurement should disclose hardware boundary, method, functional unit, time window, and software version. A precise model-call energy number without provider or independent telemetry remains an estimate.

The carbon dimension can be aligned with the Software Carbon Intensity form:

\[
SCI=(E\times I+M)/R
\]

The current core stores a declared carbon dimension but does not claim complete SCI conformance.

---

## 10. Reference implementation

The release includes:

- a bilingual standalone HTML application;
- a zero-runtime-dependency Python package;
- semantic route enumeration and Pareto selection;
- safe local builtin execution;
- outcome receipts and a hash-linked responsibility ledger;
- HMAC leases and a loopback peer server;
- market clearing and no-payment settlement proposals;
- recipe distillation and registered recipe execution;
- a loopback JSON API;
- MCP tool descriptions and stdio server;
- an A2A Agent Card;
- an OpenAPI 3.1 description;
- JSON Schemas, tests, a TLA+ draft, and an independent bounded checker.

The default demonstration selects:

```text
local-text-stats
→ local-extractive-summary
→ local-markdown-compose
```

with declared expected energy of 14.78 J, latency of 0.35 seconds, zero monetary cost, route quality of approximately 0.86, and zero external-action authority. These are demonstration assumptions, not hardware measurements.

---

## 11. Deployment patterns

### Personal computing

Use local deterministic functions for privacy-sensitive formatting, statistics, and hashing; invoke a model only where open-ended interpretation is actually required.

### Enterprise knowledge work

Connect CRM, browser research, code processing, and document systems while keeping each scope and outcome receipt explicit.

### Specialist software

Use GUI operation where necessary, but allow APIs and scripts to win when they are more reliable and less expensive after verification.

### Personal compute mesh

Borrow GPU inference, rendering, or specialist export from another owned computer through a one-capability lease.

### Capability marketplace

Purchase expert review or a specialist transformation without purchasing a full application seat, while binding settlement to acceptance evidence.

### Software-vendor transition

Expose capabilities with stable semantics, price, quality, authority, and evidence so that agents prefer the official road over GUI “off-road” automation.

---

## 12. Commercial path

The open core should retain catalogs, routing, gates, Pareto analysis, receipts, leases, local execution, schemas, and export.

Commercial layers can provide:

- enterprise capability inventory;
- identity, key, and revocation infrastructure;
- API, MCP, and GUI connectors;
- physical energy measurement;
- capability-market operations;
- service warranties and dispute handling;
- multi-node scheduling;
- private deployment and SLA;
- industry policy packs;
- audit and conformance services.

A credible pilot compares 20–50 recurring tasks under the same functional unit and quality floor, measuring completion, total time, human intervention, model calls, data egress, rework, physical energy, total cost, and user acceptance.

---

## 13. MINEX-1000

The pre-standard defines six cumulative levels:

| Level | Requirement |
|---|---|
| L0 | explicit intent, semantic inputs/outputs, and provenance |
| L1 | machine-readable capability manifests and surfaces |
| L2 | authority, quality, privacy, budget, and side-effect gates |
| L3 | Pareto routes, declared preferences, and result receipts |
| L4 | bounded leases, market proposals, recipe distillation, and successor reauthorization |
| L5 | production signatures, measured energy, revocation, payment, and independent conformance |

The reference implementation targets `L4-reference`.

---

## 14. Reality boundary

The current release does not prove that it has enumerated all routes, found a global optimum, physically measured model energy, established provider trust, created a legal marketplace, sandboxed arbitrary code, or guaranteed GUI stability. A hash-linked receipt proves recorded continuity, not the truth of every input.

Production deployment still requires hardware-backed identity, a real sandbox, network segmentation, temporary credentials, revocation, encrypted transport, calibrated measurements, payment or escrow infrastructure, jurisdiction-specific contracts, independent audit, and human escalation.

---

## Conclusion

The durable software layer of the model-first era should not become another super-app. It should make purpose, capability, authority, expenditure, and evidence explicit so that models, applications, devices, people, and markets become comparable execution surfaces without becoming interchangeable sources of power.

\[
\boxed{
IntentFirst
+CapabilityLiquidity
+AuthorityBeforeOptimization
+QualityBeforeCheapness
+ParetoBeforeWeightedScore
+MeasurementBeforeGreenClaims
+ReceiptBeforeSettlement
+ReauthorizationBeforeInheritance
+CorrectionBeforeClosure
}
\]

**When a model can replace part of an application, the decisive system is not the one that tells the user which app to open. It is the one that can show which authorized capability route satisfies the real purpose with the least verified total expenditure and the clearest path to correction.**
