from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ledger import append_event
from .util import sha256_json, write_json


def create_receipt(workspace: Path, intent: dict[str, Any], plan: dict[str, Any], execution: dict[str, Any] | None = None) -> tuple[Path, dict[str, Any]]:
    selected = plan.get("selected_route")
    receipt = {
        "receipt_type": "MINEX_EXECUTION_RECEIPT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "intent": intent,
        "intent_digest": sha256_json(intent),
        "selected_route": selected,
        "plan_digest": sha256_json(plan),
        "execution": execution,
        "execution_digest": sha256_json(execution) if execution is not None else None,
        "status": "VERIFIED_LOCAL_RESULT" if execution and execution.get("status") == "COMPLETED_LOCAL_REVERSIBLE" else "PLAN_ONLY",
        "limitations": [
            "Declared or provider-reported energy estimates are not physical measurements unless measurement_source says otherwise.",
            "A valid receipt proves the recorded route and result digest, not universal correctness.",
            "No real payment, contract, GUI action, or remote publication is executed by the reference core.",
        ],
        "automatic_external_action_authority": 0,
    }
    receipt["receipt_digest"] = sha256_json(receipt)
    path = workspace / "receipts" / f"{receipt['receipt_digest'][:20]}.json"
    write_json(path, receipt)
    append_event(workspace / "responsibility-ledger.jsonl", "receipt.created", {
        "receipt_digest": receipt["receipt_digest"], "status": receipt["status"]
    })
    return path, receipt
