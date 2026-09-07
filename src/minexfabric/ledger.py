from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .util import canonical_json, sha256_json

GENESIS = "0" * 64


def append_event(path: Path, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    previous = GENESIS
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            previous = json.loads(lines[-1])["event_digest"]
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
        "previous_digest": previous,
    }
    event["event_digest"] = sha256_json(event)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(event) + "\n")
    return event


def verify_ledger_text(text: str) -> dict[str, Any]:
    previous = GENESIS
    count = 0
    for index, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            return {"valid": False, "events": count, "error": f"invalid_json_line_{index}"}
        digest = event.pop("event_digest", None)
        if event.get("previous_digest") != previous:
            return {"valid": False, "events": count, "error": f"broken_link_line_{index}"}
        expected = sha256_json(event)
        if digest != expected:
            return {"valid": False, "events": count, "error": f"digest_mismatch_line_{index}"}
        previous = digest
        count += 1
    return {"valid": True, "events": count, "last_digest": previous}


def verify_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"valid": True, "events": 0, "last_digest": GENESIS}
    return verify_ledger_text(path.read_text(encoding="utf-8"))
