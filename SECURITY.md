# Security Policy

## Supported version

The current research release is `1.0.x`.

## Reporting

Report vulnerabilities privately to the repository owner before public disclosure. Include the affected version, a minimal reproduction, expected impact, and whether the issue crosses an authority boundary.

## Security model

The reference core deliberately has no automatic authority to trade, pay, contract, publish, or invoke arbitrary remote systems. Local builtin execution is allowlisted. The local planning API is loopback-only by default. The peer executor requires a bounded signed lease.

Running untrusted code or GUI automation requires an independent sandbox or virtual machine, resource limits, temporary credentials, and separate review. MINEX route selection is not an operating-system sandbox.
