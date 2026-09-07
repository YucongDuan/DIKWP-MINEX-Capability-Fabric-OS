from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .models import CapabilityManifest, CostVector
from .util import clamp


DIMENSIONS = (
    "expected_energy_j", "latency_ms", "money", "human_minutes",
    "data_exposure", "carbon_g", "semantic_loss", "failure_probability",
)


def combine_probabilities(values: Iterable[float]) -> float:
    survival = 1.0
    for value in values:
        survival *= 1.0 - clamp(value)
    return clamp(1.0 - survival)


def aggregate_cost(capabilities: Iterable[CapabilityManifest]) -> CostVector:
    caps = list(capabilities)
    if not caps:
        return CostVector()
    data_exposure = combine_probabilities(cap.cost.data_exposure for cap in caps)
    semantic_loss = combine_probabilities(cap.cost.semantic_loss for cap in caps)
    failure_probability = combine_probabilities(cap.cost.failure_probability for cap in caps)
    return CostVector(
        energy_j=sum(cap.cost.energy_j for cap in caps),
        verification_energy_j=sum(cap.cost.verification_energy_j for cap in caps),
        coordination_energy_j=sum(cap.cost.coordination_energy_j for cap in caps),
        retry_energy_j=sum(cap.cost.retry_energy_j for cap in caps),
        latency_ms=sum(cap.cost.latency_ms for cap in caps),
        money=sum(cap.cost.money for cap in caps),
        human_minutes=sum(cap.cost.human_minutes for cap in caps),
        data_exposure=data_exposure,
        carbon_g=sum(cap.cost.carbon_g for cap in caps),
        semantic_loss=semantic_loss,
        failure_probability=failure_probability,
        measurement_source="mixed" if len({cap.cost.measurement_source for cap in caps}) > 1 else caps[0].cost.measurement_source,
    )


def cost_metrics(cost: CostVector) -> dict[str, float | str]:
    data = asdict(cost)
    data["expected_energy_j"] = cost.expected_energy_j
    return data


def route_quality(capabilities: Iterable[CapabilityManifest], cost: CostVector) -> float:
    caps = list(capabilities)
    if not caps:
        return 0.0
    bottleneck = min(cap.quality for cap in caps)
    return clamp(bottleneck * (1.0 - cost.semantic_loss) * (1.0 - 0.35 * cost.failure_probability))


def normalized_score(metrics: dict[str, float | str], weights: dict[str, float], references: dict[str, float]) -> float:
    score = 0.0
    for dimension, weight in weights.items():
        if weight <= 0:
            continue
        raw = float(metrics.get(dimension, 0.0))
        reference = max(float(references.get(dimension, 1.0)), 1e-9)
        ratio = raw / reference
        # Soft saturation prevents one unbounded metric from hiding all structure.
        normalized = ratio / (1.0 + ratio)
        score += weight * normalized
    return float(score)


def dominates(a: dict[str, float | str], b: dict[str, float | str], a_quality: float, b_quality: float) -> bool:
    no_worse = a_quality >= b_quality
    strictly_better = a_quality > b_quality
    for dimension in DIMENSIONS:
        av = float(a.get(dimension, 0.0))
        bv = float(b.get(dimension, 0.0))
        no_worse = no_worse and av <= bv + 1e-12
        strictly_better = strictly_better or av < bv - 1e-12
    return no_worse and strictly_better
