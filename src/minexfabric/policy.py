from __future__ import annotations

from typing import Iterable

from .costs import cost_metrics
from .models import CapabilityManifest, IntentSpec, SIDE_EFFECT_ORDER, Surface


DEFAULT_REFERENCES = {
    "expected_energy_j": 1000.0,
    "latency_ms": 60_000.0,
    "money": 1.0,
    "human_minutes": 30.0,
    "data_exposure": 1.0,
    "carbon_g": 100.0,
    "semantic_loss": 1.0,
    "failure_probability": 1.0,
}


def evaluate_route(intent: IntentSpec, capabilities: Iterable[CapabilityManifest], metrics: dict, quality: float) -> list[str]:
    caps = list(capabilities)
    c = intent.constraints
    reasons: list[str] = []
    if not caps:
        reasons.append("EMPTY_ROUTE")
        return reasons
    if any(not cap.availability for cap in caps):
        reasons.append("CAPABILITY_UNAVAILABLE")
    granted = set(intent.granted_scopes)
    for cap in caps:
        missing = set(cap.authority_scopes) - granted
        if missing:
            reasons.append(f"MISSING_AUTHORITY:{cap.capability_id}:{','.join(sorted(missing))}")
    allowed_surfaces = set(c.get("allowed_surfaces", [surface.value for surface in Surface]))
    for cap in caps:
        if cap.surface not in allowed_surfaces:
            reasons.append(f"SURFACE_NOT_ALLOWED:{cap.capability_id}:{cap.surface}")
        if cap.surface == Surface.SAME_OWNER_PEER.value and cap.owner_realm != intent.owner_realm:
            reasons.append(f"PEER_OWNER_REALM_MISMATCH:{cap.capability_id}")
        if cap.surface == Surface.MARKET_SERVICE.value and not bool(c.get("external_purchase_allowed", False)):
            reasons.append(f"EXTERNAL_PURCHASE_NOT_ALLOWED:{cap.capability_id}")
        if cap.surface in {Surface.SAME_OWNER_PEER.value, Surface.MARKET_SERVICE.value} and not bool(c.get("network_allowed", False)):
            reasons.append(f"NETWORK_NOT_ALLOWED:{cap.capability_id}")
    max_side_effect = str(c.get("max_side_effect", "reversible_local"))
    max_side_effect_order = SIDE_EFFECT_ORDER.get(max_side_effect, 1)
    for cap in caps:
        if SIDE_EFFECT_ORDER.get(cap.side_effect, 99) > max_side_effect_order:
            reasons.append(f"SIDE_EFFECT_TOO_HIGH:{cap.capability_id}:{cap.side_effect}")
    limits = {
        "max_expected_energy_j": "expected_energy_j",
        "max_latency_ms": "latency_ms",
        "max_money": "money",
        "max_human_minutes": "human_minutes",
        "max_data_exposure": "data_exposure",
        "max_carbon_g": "carbon_g",
        "max_semantic_loss": "semantic_loss",
        "max_failure_probability": "failure_probability",
    }
    for constraint_name, metric_name in limits.items():
        if constraint_name in c and float(metrics.get(metric_name, 0.0)) > float(c[constraint_name]) + 1e-12:
            reasons.append(f"BUDGET_EXCEEDED:{metric_name}")
    min_quality = float(c.get("min_quality", 0.0))
    if quality + 1e-12 < min_quality:
        reasons.append("QUALITY_BELOW_MINIMUM")
    return sorted(set(reasons))


def references_for_intent(intent: IntentSpec) -> dict[str, float]:
    references = dict(DEFAULT_REFERENCES)
    custom = intent.constraints.get("normalization_references", {})
    references.update({str(k): float(v) for k, v in custom.items()})
    return references
