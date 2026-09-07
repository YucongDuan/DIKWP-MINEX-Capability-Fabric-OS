from minexfabric.demo import demo_catalog, demo_intent
from minexfabric.models import IntentSpec, manifests_from_iterable
from minexfabric.planner import enumerate_routes, select_route


def setup_data():
    return IntentSpec.from_dict(demo_intent()), manifests_from_iterable(demo_catalog())


def test_demo_selects_local_composed_route():
    intent, catalog = setup_data()
    selected = select_route(intent, catalog)["selected_route"]
    assert selected is not None
    assert selected["capability_ids"] == ["local-extractive-summary", "local-text-stats", "local-markdown-compose"]


def test_external_routes_are_rejected_by_default():
    intent, catalog = setup_data()
    routes = enumerate_routes(intent, catalog)
    rejected = [r for r in routes if "market-certified-brief" in r.capability_ids]
    assert rejected
    assert any(any("EXTERNAL_PURCHASE_NOT_ALLOWED" in reason or "NETWORK_NOT_ALLOWED" in reason for reason in r.gate_reasons) for r in rejected)


def test_missing_authority_rejects_api():
    intent_dict = demo_intent()
    intent_dict["granted_scopes"] = ["data.read"]
    routes = enumerate_routes(IntentSpec.from_dict(intent_dict), manifests_from_iterable(demo_catalog()))
    api = next(r for r in routes if r.capability_ids == ["local-api-brief"])
    assert not api.admissible
    assert any(reason.startswith("MISSING_AUTHORITY") for reason in api.gate_reasons)


def test_network_and_market_can_be_enabled():
    intent_dict = demo_intent()
    intent_dict["constraints"]["network_allowed"] = True
    intent_dict["constraints"]["external_purchase_allowed"] = True
    intent_dict["constraints"]["max_side_effect"] = "reversible_external"
    intent_dict["constraints"]["max_data_exposure"] = 0.6
    intent_dict["granted_scopes"] += ["peer.invoke", "market.purchase", "human.delegate"]
    routes = enumerate_routes(IntentSpec.from_dict(intent_dict), manifests_from_iterable(demo_catalog()))
    assert any(r.admissible and "market-certified-brief" in r.capability_ids for r in routes)


def test_no_route_expands_authority():
    intent, catalog = setup_data()
    result = select_route(intent, catalog)
    assert result["authority_invariant"] == "NO_ROUTE_MAY_EXPAND_GRANTED_AUTHORITY"
    assert result["automatic_external_action_authority"] == 0
