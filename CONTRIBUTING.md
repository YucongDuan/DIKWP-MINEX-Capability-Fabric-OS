# Contributing

Contributions are welcome in the following high-value areas:

1. measured energy adapters with disclosed hardware and functional units;
2. safe deterministic capability handlers;
3. language-specific capability manifests;
4. MCP and A2A interoperability profiles;
5. lease revocation and hardware-backed signing;
6. reproducible route-quality benchmarks;
7. protected tests showing when model-native, API, code, GUI, peer, or human routes should *not* be selected.

Every pull request should state:

- the semantic input and output types affected;
- new authority scopes, if any;
- measurement source for each cost estimate;
- failure and rollback behavior;
- tests and limitations;
- whether any external side effect was introduced.

Do not add automatic payment, contract, remote publication, secret access, or unrestricted shell execution to the reference core.
