from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable

from .costs import aggregate_cost, cost_metrics, dominates, normalized_score, route_quality
from .models import CapabilityManifest, IntentSpec, RoutePlan
from .policy import evaluate_route, references_for_intent
from .util import sha256_json


@dataclass(frozen=True)
class _Node:
    types: frozenset[str]
    route: tuple[str, ...]


def _plan_id(intent: IntentSpec, route: tuple[str, ...]) -> str:
    return "route-" + sha256_json({"intent": intent.intent_id, "route": list(route)})[:16]


def enumerate_routes(intent: IntentSpec, catalog: Iterable[CapabilityManifest], max_steps: int = 6, max_routes: int = 5000) -> list[RoutePlan]:
    manifests = list(catalog)
    by_id = {cap.capability_id: cap for cap in manifests}
    initial = frozenset(intent.available_types)
    required = set(intent.required_types)
    queue: deque[_Node] = deque([_Node(initial, ())])
    seen: set[tuple[frozenset[str], tuple[str, ...]]] = {(initial, ())}
    candidates: list[RoutePlan] = []
    references = references_for_intent(intent)

    while queue and len(seen) <= max_routes:
        node = queue.popleft()
        if required.issubset(node.types) and node.route:
            caps = [by_id[item] for item in node.route]
            cost = aggregate_cost(caps)
            metrics = cost_metrics(cost)
            quality = route_quality(caps, cost)
            reasons = evaluate_route(intent, caps, metrics, quality)
            candidates.append(RoutePlan(
                route_id=_plan_id(intent, node.route),
                capability_ids=list(node.route),
                final_types=sorted(node.types),
                cost=metrics,
                quality=quality,
                score=normalized_score(metrics, intent.weights, references),
                admissible=not reasons,
                gate_reasons=reasons,
            ))
            # Keep exploring: a longer route can reduce cost through a specialized route only if manifests model that.
        if len(node.route) >= max_steps:
            continue
        for cap in manifests:
            if cap.capability_id in node.route or not cap.availability:
                continue
            if not set(cap.requires).issubset(node.types):
                continue
            next_types = frozenset(set(node.types).union(cap.provides))
            if next_types == node.types:
                continue
            next_route = node.route + (cap.capability_id,)
            marker = (next_types, next_route)
            if marker not in seen:
                seen.add(marker)
                queue.append(_Node(next_types, next_route))

    admissible = [item for item in candidates if item.admissible]
    for candidate in admissible:
        candidate.pareto = not any(
            other.route_id != candidate.route_id
            and dominates(other.cost, candidate.cost, other.quality, candidate.quality)
            for other in admissible
        )
    candidates.sort(key=lambda item: (not item.admissible, not item.pareto, item.score, len(item.capability_ids), item.route_id))
    return candidates


def select_route(intent: IntentSpec, catalog: Iterable[CapabilityManifest], max_steps: int = 6) -> dict:
    routes = enumerate_routes(intent, catalog, max_steps=max_steps)
    pareto = [item for item in routes if item.admissible and item.pareto]
    selected = min(pareto, key=lambda item: (item.score, -item.quality, len(item.capability_ids))) if pareto else None
    return {
        "intent": intent.to_dict(),
        "intent_digest": intent.digest,
        "selected_route": selected.to_dict() if selected else None,
        "pareto_routes": [item.to_dict() for item in pareto],
        "all_routes": [item.to_dict() for item in routes],
        "route_count": len(routes),
        "admissible_count": sum(1 for item in routes if item.admissible),
        "pareto_count": len(pareto),
        "authority_invariant": "NO_ROUTE_MAY_EXPAND_GRANTED_AUTHORITY",
        "automatic_external_action_authority": 0,
    }
