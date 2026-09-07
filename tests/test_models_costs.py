from minexfabric.costs import aggregate_cost, cost_metrics, dominates, normalized_score, route_quality
from minexfabric.demo import demo_catalog
from minexfabric.models import CostVector, IntentSpec, manifests_from_iterable


def test_expected_energy_includes_retry():
    cost = CostVector(energy_j=10, verification_energy_j=2, retry_energy_j=12, failure_probability=0.2)
    assert abs(cost.expected_energy_j - 15) < 1e-9


def test_aggregate_cost_combines_risk_not_sum():
    caps = manifests_from_iterable(demo_catalog()[:2])
    cost = aggregate_cost(caps)
    assert 0 < cost.failure_probability < sum(c.cost.failure_probability for c in caps)
    assert cost.energy_j == 902


def test_route_quality_has_bottleneck():
    caps = manifests_from_iterable(demo_catalog()[1:4])
    cost = aggregate_cost(caps)
    quality = route_quality(caps, cost)
    assert 0.80 < quality < 0.94


def test_normalized_score_is_bounded():
    score = normalized_score({"expected_energy_j": 10}, {"expected_energy_j": 1.0}, {"expected_energy_j": 10})
    assert 0 < score < 1


def test_pareto_dominance():
    a = {"expected_energy_j": 10, "latency_ms": 10, "money": 0, "human_minutes": 0, "data_exposure": 0, "carbon_g": 0, "semantic_loss": 0, "failure_probability": 0}
    b = dict(a); b["expected_energy_j"] = 20
    assert dominates(a, b, 0.9, 0.9)
