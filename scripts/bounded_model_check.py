from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import asdict, dataclass, replace
from pathlib import Path

ROUTES = ("local", "peer", "market", "gui")
PHASES = (
    "DRAFT",
    "PLANNED",
    "PROPOSAL_ONLY",
    "EXECUTED",
    "VERIFIED",
    "SETTLEMENT_PROPOSED",
    "STOPPED",
)


@dataclass(frozen=True)
class State:
    phase: str = "DRAFT"
    route: str = "none"
    authority_granted: bool = False
    lease_valid: bool = False
    successor: bool = False
    successor_reauthorized: bool = False
    receipt_valid: bool = False
    settlement_proposed: bool = False
    payment_executed: bool = False
    external_action_executed: bool = False
    external_action_authority: int = 0
    stopped: bool = False


def transitions(s: State) -> list[State]:
    out: list[State] = []
    if not s.stopped:
        out.append(replace(s, phase="STOPPED", stopped=True, lease_valid=False))

    if s.phase == "DRAFT" and not s.stopped:
        for route in ROUTES:
            out.append(replace(s, phase="PLANNED", route=route))
        return out

    if s.phase == "PLANNED" and not s.stopped:
        if not s.authority_granted:
            out.append(replace(s, authority_granted=True))
        if s.route == "peer" and s.authority_granted and not s.lease_valid:
            out.append(replace(s, lease_valid=True))
        if s.route == "peer" and not s.successor:
            # A successor sees predecessor artifacts, but the lease is invalidated.
            out.append(replace(s, successor=True, lease_valid=False, successor_reauthorized=False))
        if s.route == "peer" and s.successor and s.authority_granted and not s.successor_reauthorized:
            out.append(replace(s, successor_reauthorized=True, lease_valid=True))

        if s.route == "local" and s.authority_granted:
            out.append(replace(s, phase="EXECUTED"))
        elif s.route == "peer" and s.authority_granted and s.lease_valid and (not s.successor or s.successor_reauthorized):
            out.append(replace(s, phase="EXECUTED"))
        elif s.route in {"market", "gui"} and s.authority_granted:
            # The reference implementation can prepare an externally reviewed proposal only.
            out.append(replace(s, phase="PROPOSAL_ONLY"))
        return out

    if s.phase == "EXECUTED" and not s.stopped:
        out.append(replace(s, phase="VERIFIED", receipt_valid=True))
        return out

    if s.phase == "VERIFIED" and s.receipt_valid and not s.stopped:
        out.append(replace(s, phase="SETTLEMENT_PROPOSED", settlement_proposed=True))
        return out

    return out


def violations(s: State) -> list[str]:
    result: list[str] = []
    if s.external_action_authority != 0:
        result.append("EXTERNAL_AUTHORITY_NONZERO")
    if s.payment_executed:
        result.append("AUTOMATIC_PAYMENT_OCCURRED")
    if s.external_action_executed:
        result.append("AUTOMATIC_EXTERNAL_ACTION_OCCURRED")
    if s.stopped and s.phase != "STOPPED":
        result.append("NONSTOP_PHASE_AFTER_STOP")
    if s.phase in {"EXECUTED", "VERIFIED", "SETTLEMENT_PROPOSED"} and not s.authority_granted:
        result.append("EXECUTION_WITHOUT_AUTHORITY")
    if s.phase in {"EXECUTED", "VERIFIED", "SETTLEMENT_PROPOSED"} and s.route == "peer":
        if not s.lease_valid:
            result.append("PEER_EXECUTION_WITHOUT_VALID_LEASE")
        if s.successor and not s.successor_reauthorized:
            result.append("SUCCESSOR_INHERITED_AUTHORITY")
    if s.route in {"market", "gui"} and s.phase in {"EXECUTED", "VERIFIED"}:
        result.append("REFERENCE_CORE_EXECUTED_EXTERNAL_ROUTE")
    if s.phase == "SETTLEMENT_PROPOSED" and not s.receipt_valid:
        result.append("SETTLEMENT_WITHOUT_RECEIPT")
    if s.settlement_proposed and s.phase not in {"SETTLEMENT_PROPOSED", "STOPPED"}:
        result.append("SETTLEMENT_FLAG_PHASE_MISMATCH")
    return result


def run() -> dict:
    start = State()
    queue = deque([(start, 0)])
    seen = {start}
    checked = 0
    max_depth = 0
    violations_found: list[dict] = []
    while queue:
        state, depth = queue.popleft()
        max_depth = max(max_depth, depth)
        for violation in violations(state):
            violations_found.append({"state": asdict(state), "violation": violation})
        for nxt in transitions(state):
            checked += 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, depth + 1))

    negative_controls = [
        replace(start, phase="EXECUTED", route="local"),
        replace(start, phase="EXECUTED", route="peer", authority_granted=True, successor=True),
        replace(start, phase="EXECUTED", route="market", authority_granted=True),
        replace(start, phase="SETTLEMENT_PROPOSED", route="local", authority_granted=True, settlement_proposed=True),
        replace(start, phase="STOPPED", stopped=True, payment_executed=True),
    ]
    negative_results = [
        {"state": asdict(state), "detected": violations(state)} for state in negative_controls
    ]
    negative_controls_passed = all(item["detected"] for item in negative_results)

    return {
        "model": "MINEX_BOUNDED_CAPABILITY_LIFECYCLE",
        "reachable_states": len(seen),
        "checked_transitions": checked,
        "max_shortest_path_depth": max_depth,
        "invariant_violations": violations_found,
        "negative_controls": negative_results,
        "negative_controls_passed": negative_controls_passed,
        "passed": not violations_found and negative_controls_passed,
        "local_verified_state_reachable": any(s.phase == "VERIFIED" and s.route == "local" for s in seen),
        "peer_verified_state_reachable": any(s.phase == "VERIFIED" and s.route == "peer" for s in seen),
        "external_proposal_state_reachable": any(s.phase == "PROPOSAL_ONLY" for s in seen),
        "settlement_proposal_reachable": any(s.phase == "SETTLEMENT_PROPOSED" for s in seen),
        "stopped_state_reachable": any(s.phase == "STOPPED" for s in seen),
        "scope": "Finite reference lifecycle only; not a proof for arbitrary integrations, physical energy claims, or external providers.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(Path(__file__).resolve().parents[1] / "validation" / "BOUNDED_MODEL_CHECK_RECEIPT.json"))
    args = parser.parse_args()
    result = run()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
