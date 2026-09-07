# MINEX-1000 Conformance Test Plan

## Structural tests

- validate intent, capability, plan, receipt, and lease schemas;
- reject missing required identifiers and semantic types;
- reject duplicate capability identifiers;
- verify supported surface and side-effect enumerations.

## Authority tests

- a missing scope rejects the route;
- network and purchase routes require explicit flags;
- peer owner-realm mismatch rejects the route;
- external-action authority must remain zero in reference outputs;
- successor artifacts cannot activate a lease.

## Cost and optimization tests

- expected energy includes retry cost;
- failure and exposure combine monotonically;
- Pareto dominance requires no worse cost and quality;
- weighted score is not applied to rejected routes;
- changing weights can change the selected Pareto point without changing admissibility.

## Execution tests

- safe local builtin route completes;
- non-builtin route remains proposal-only;
- malformed recipe fails closed;
- recursive recipe is rejected;
- output and route digests are stable for deterministic inputs.

## Lease and market tests

- valid HMAC lease verifies;
- tampered, expired, exhausted, or mismatched lease fails;
- market filters output mismatch, unavailable bid, price excess, and owner-realm mismatch;
- settlement remains proposal-only.

## Distribution tests

- source tree, Wheel, PYZ, extracted source ZIP, and cloned Git Bundle produce the same normalized demo result;
- browser application plans a route without external network requests;
- local API rejects caller-selected catalog paths;
- MCP tool list and plan call function.
