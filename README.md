# DIKWP MINEX Capability Fabric OS

Created by Yucong Duan (段玉聪).

> Intent first. Apps optional. Capabilities liquid. Proof before execution.

DIKWP MINEX is an offline-first, open-source capability router for the model-first computing era. It accepts an intended outcome and selects a valid route across model-native reasoning, deterministic code, APIs, GUI automation, same-owner peer computers, paid capability providers, human delegates, and verified reusable recipes.

MINEX does not assume that a dedicated app is always necessary. It also does not assume that the model should always do everything itself. It first rejects routes that violate authority, quality, privacy, budget, side-effect, or reversibility constraints; then it exposes the Pareto frontier and selects the lowest declared verified execution expenditure.

```text
Operating mode:
MESH95_INTENT_CAPABILITY_PARETO_MINIMUM_EXPENDITURE_LEASE_RECEIPT_CLOSURE

Pre-standard:
MINEX-1000:2026-DRAFT
Minimum Verified Execution Expenditure Capability Protocol

License:
Apache-2.0

Automatic external-action authority: 0
Automatic payment authority: 0
Automatic contract authority: 0
Automatic remote-publication authority: 0
```

## Why now

Frontier models increasingly combine reasoning, generated code, API and MCP tool use, browsers, and direct computer use. As graphical interfaces become viable machine interfaces, the app stops being the mandatory point of navigation. It remains important as a system of record, permission boundary, specialist runtime, and verified executor.

MINEX makes the next architectural layer explicit:

```text
intent
→ semantic input/output types
→ capability discovery
→ authority and quality gates
→ candidate route composition
→ Pareto frontier
→ minimum verified expenditure selection
→ local execution or bounded proposal
→ outcome receipt
→ optional recipe distillation
```

## Direct use

Open the self-contained bilingual application:

```text
DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.html
```

It needs no account, API key, server, or network connection.

## Quick start

```bash
python DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.pyz \
  demo --workspace .minex-demo --reset
```

Plan a route:

```bash
minex plan \
  examples/intents/model-first-brief.json \
  examples/catalog/default-capabilities.json \
  --output plan.json
```

Execute the selected route when every step is a registered safe local builtin:

```bash
minex execute \
  examples/intents/model-first-brief.json \
  examples/catalog/default-capabilities.json \
  --workspace .minex-run
```

Generate a reusable recipe from a verified receipt:

```bash
minex distill .minex-run/receipts/<receipt>.json \
  --id recipe-local-brief-v1 \
  --output recipe.json
```

## Capability surfaces

| Surface | Meaning | Reference-core execution |
|---|---|---|
| `model_native` | A model directly produces the semantic result | Provider adapter required |
| `local_code` | Deterministic or bounded local code | Builtins supported |
| `local_api` | A formal local app/service interface | Adapter required |
| `local_gui` | Browser or desktop interface operation | Proposal/adapter required |
| `same_owner_peer` | Borrow a capability from another authorized node | HMAC lease and peer server included |
| `market_service` | Purchase a result from a provider | Clearing and settlement proposal only |
| `human_delegate` | Named human capability | Proposal only |
| `recipe` | Distilled verified capability sequence | Local registered recipes supported |

## Core mathematics

For a route \(\rho\), MINEX keeps costs in separate units:

\[
\mathbf C(\rho)=
(E, T, M, H, X, G, L, P_f)
\]

where the dimensions are expected physical energy, latency, money, human attention, data exposure, carbon, semantic loss, and failure probability.

Expected physical energy includes retries:

\[
E_{exp}
=
E_{exec}+E_{verify}+E_{coord}
+
\frac{p_f}{1-p_f}E_{retry}
\]

The system first filters invalid routes and computes a Pareto frontier. Only then does it apply the user-declared normalized preference weights. Unlike a single opaque score, no route can compensate for missing authority or inadequate quality by being cheap.

## Cross-device capability borrowing

A lease binds:

```text
capability
provider
consumer
owner realm
expiry
call budget
money budget
external authority = 0
HMAC signature
```

The reference peer server exposes only registered safe builtins. A lease never implies broader access to the peer device.

## Paid capability exchange

The market module can compare offers by output type, price, expected energy, quality, availability, and owner-realm restrictions. It creates a settlement proposal bound to a result receipt. It does not move money.

## Procedural internalization

MINEX can distill a successful verified route into a reusable recipe. This is operational compression, not literal weight modification:

```text
trace + typed inputs/outputs + authority + result receipt
→ reusable recipe manifest
```

The recipe reduces planning and coordination overhead but cannot inherit undocumented permissions, copy proprietary implementations, or silently call external systems.

## Safety boundary

- Interface access never creates authorization.
- A model is not the sole enforcement point for permissions.
- No external payment, contract, publication, or remote action is executed by the reference core.
- Peer and market routes require explicit policy permission.
- Successor agents do not inherit leases or authority from predecessor artifacts.
- Declared energy values remain estimates unless accompanied by a measurement receipt.

## Repository map

```text
src/minexfabric/       reference implementation
examples/              catalog, intent and market examples
schemas/               JSON Schema 2020-12 assets
interop/               generated MCP, A2A and OpenAPI descriptions
formal/                 TLA+ draft and bounded model checker
spec/                   MINEX-1000 draft standard
scripts/                audit, model check and SBOM generation
validation/             reproducible receipts
```

## Documentation

- [Chinese system report](docs/SYSTEM_REPORT_CN.md)
- [English system report](docs/SYSTEM_REPORT_EN.md)
- [Bilingual methodology](docs/METHODOLOGY_CN_EN.md)
- [Security and authority model](docs/SECURITY_AND_AUTHORITY_CN_EN.md)
- [Deployment playbook](docs/DEPLOYMENT_PLAYBOOK_CN_EN.md)
- [GitHub launch playbook](docs/GITHUB_LAUNCH_PLAYBOOK_CN_EN.md)
- [Source register](docs/SOURCE_REGISTER.md)
- [MINEX-1000 draft](spec/MINEX_1000_CORE_SPEC_DRAFT_CN_EN.md)

## Current status

`RESEARCH_ALPHA_REFERENCE_IMPLEMENTATION`

The system demonstrates a capability-routing protocol and safe local execution. It is not a universal energy meter, a legal marketplace, a payment system, a desktop sandbox, or proof that a selected route is universally correct.

### Peer hardening in v1.0.0

The peer reference server additionally enforces replay identifiers, server-side call budgets, provider/consumer/owner-realm binding, request-size limits, and a prohibition on remote path inputs. The MCP ledger tool verifies supplied ledger content rather than reading an arbitrary caller-selected local path.

## Complete delivery materials

The `delivery/` directory preserves the supplied bilingual start pack, standalone application, reports, draft standardization assets, validation receipts, and supply-chain records. The browsable reference source remains at the repository root.

## Portfolio connections

- [DIKWP MINEX Fabric OS](https://github.com/YucongDuan/DIKWP-MINEX-FABRIC-OS) — a complementary minimum-energy runtime with evidence ledgers, federation, and dry-run exchange.
- [DIKWP AGI Continuity Ark OS](https://github.com/YucongDuan/DIKWP-AGI-Continuity-Ark-OS) — personal and household continuity planning across plural AGI futures.
- [DIKWP HUMAN CONTINUITY ARK / SHENGZHOU 28.0.0](https://github.com/YucongDuan/DIKWP-HUMAN-CONTINUITY-ARK-SHENGZHOU-28.0.0) — twelve-floor resilience and offline continuity operations.
- [Yucong Duan research homepage](https://yucong-duan-research.dikwp407.chatgpt.site) and [complete repository ecosystem](https://github.com/YucongDuan/YucongDuan) — wider DIKWP, semantic mathematics, artificial consciousness, governance, and practice programme.

A portfolio link records research continuity or semantic proximity. It does not by itself establish a runtime dependency, interoperability, external adoption, institutional endorsement, or shared legal status.

## Dedication

This project is dedicated to Duan Dikweipu (段迪克维普) as a statement of care for a future in which human purpose, dignity, and continuity remain protected. This dedication does not assign authorship, ownership, operational authority, endorsement, or legal responsibility to the dedicatee.

## Current interface presentation

[Open the interface source](DIKWP_MINEX_CAPABILITY_FABRIC_OS_v1.0.0.html) from the current repository download. See [interface and authorship notes](INTERFACE_NOTES.md) for English coverage, report generation and validation scope.
