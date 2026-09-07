# Security and Authority Model / 安全与权限模型

## Constitutional invariants / 宪法性不变量

1. Interface accessibility never grants authority. / 能看见或能点击不等于获得授权。
2. A route cannot expand the scopes declared in the intent. / 路线不得扩大意图中已授予的权限。
3. A successor agent cannot inherit authority from an artifact. / 后继Agent不得从前代工件继承权限。
4. Real payment, contract, voting, asset transfer, and remote publication remain external. / 真实付款、签约、投票、资产转移和远端发布不在参考内核执行。
5. No route is selected solely because it is cheap. / 不得仅因低价选择路线。
6. Failed or adverse evidence remains in the ledger. / 失败与不利证据不得被静默删除。

## Threat model / 威胁模型

- malicious or compromised capability provider;
- stale capability description;
- hidden data exfiltration;
- GUI prompt injection or state confusion;
- overbroad peer lease;
- inherited Agent artifact carrying obsolete authority;
- market result delivered without quality evidence;
- model hallucinating that a proposal was executed;
- falsified energy or carbon claims;
- local API path traversal or arbitrary file access.

## Reference-core mitigations / 参考实现措施

- allowlisted builtin handlers;
- `shell=false` by design: no arbitrary shell executor;
- loopback-only planning API by default;
- HTTP caller cannot choose a local catalog path;
- signed, expiring, call-bounded peer leases;
- market settlement remains proposal-only;
- hash-linked result and responsibility receipts;
- explicit `external_action_authority = 0` in manifests and outputs;
- registered-recipe expansion with recursion checks;
- static audit for dangerous execution and network primitives.

## Production requirements / 生产要求

- hardware-backed keys or managed KMS/HSM;
- mutual TLS or equivalent authenticated encrypted transport;
- revocation and short-lived credentials;
- operating-system or container sandboxing;
- data classification and purpose limitation;
- independent output validation;
- rate and monetary limits;
- human approval for consequential external actions;
- incident response across tasks, leases, caches, credentials, and successor manifests.

## Replay and local-file boundaries / 重放与本地文件边界

- Peer execution binds the lease to the capability, provider, consumer, owner realm, expiry and server-side call counter.
- Every peer request carries a bounded request identifier; replayed identifiers are rejected.
- Remote peer inputs ending in `.path` are rejected by the reference server, so a capability caller cannot turn a data-processing function into arbitrary peer-file access.
- MCP ledger verification accepts ledger content rather than a caller-selected filesystem path.
- API and peer request bodies are bounded to 1 MiB; MCP messages are bounded to 2 MiB.

- 跨设备执行把租约绑定到能力、提供者、消费者、主体域、期限和服务端调用计数。
- 每次远程请求具有有界请求标识，重复请求会被拒绝。
- 参考节点拒绝以 `.path` 结尾的远程输入，防止调用者把数据处理能力变成任意本机文件读取。
- MCP 账本检查接收账本文本，而不接收调用方指定的任意文件路径。
- API 与节点请求体限制为 1 MiB，MCP 消息限制为 2 MiB。
