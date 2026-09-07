from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .util import MinExError, sha256_json


def distill_receipt(receipt: dict[str, Any], new_capability_id: str, name: str | None = None) -> dict[str, Any]:
    if receipt.get("status") != "VERIFIED_LOCAL_RESULT":
        raise MinExError("Only a verified local result can be distilled")
    route = receipt.get("selected_route") or {}
    capability_ids = list(route.get("capability_ids", []))
    if not capability_ids:
        raise MinExError("Receipt has no route to distill")
    execution = receipt.get("execution") or {}
    if execution.get("status") != "COMPLETED_LOCAL_REVERSIBLE":
        raise MinExError("Only a completed local reversible execution can be distilled")
    output_keys = sorted(set((execution.get("outputs") or {}).keys()) - set((receipt.get("intent") or {}).get("inputs", {}).keys()))
    manifest = {
        "capability_id": new_capability_id,
        "name": name or f"Distilled recipe for {receipt.get('intent', {}).get('title', new_capability_id)}",
        "description": "A reusable recipe distilled from a verified route. It reduces planning and coordination overhead; it does not modify model weights or expand authority.",
        "provider_id": "local-distiller",
        "owner_realm": (receipt.get("intent") or {}).get("owner_realm", "local-owner"),
        "surface": "recipe",
        "requires": list((receipt.get("intent") or {}).get("available_types", [])),
        "provides": output_keys or list((receipt.get("intent") or {}).get("required_types", [])),
        "cost": dict((route.get("cost") or {})),
        "quality": float(route.get("quality", 0.0)),
        "authority_scopes": [],
        "side_effect": "reversible_local",
        "deterministic": bool(execution.get("steps")) and all(
            step.get("status") == "COMPLETED_LOCAL_REVERSIBLE" and bool(step.get("deterministic", False))
            for step in execution.get("steps", [])
        ),
        "cacheable": True,
        "availability": True,
        "executor": {"kind": "recipe", "steps": capability_ids},
        "terms": {"external_action_authority": 0},
        "provenance": {
            "distilled_at": datetime.now(timezone.utc).isoformat(),
            "source_receipt_digest": receipt.get("receipt_digest"),
            "route_digest": sha256_json(capability_ids),
        },
    }
    # Distillation only reduces future coordination overhead, never execution or verification estimates.
    manifest["cost"]["coordination_energy_j"] = float(manifest["cost"].get("coordination_energy_j", 0.0)) * 0.3
    manifest["cost"]["latency_ms"] = float(manifest["cost"].get("latency_ms", 0.0)) * 0.9
    manifest["cost"].pop("expected_energy_j", None)
    return manifest
