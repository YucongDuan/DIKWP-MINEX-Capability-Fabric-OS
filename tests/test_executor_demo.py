from pathlib import Path

from minexfabric.demo import demo_catalog, demo_intent, run_demo
from minexfabric.executor import execute_capability, execute_route
from minexfabric.models import IntentSpec, manifests_from_iterable
from minexfabric.planner import select_route


def test_builtin_text_stats():
    cap = manifests_from_iterable(demo_catalog())[1]
    result = execute_capability(cap, {"text.raw": "one two two"})
    assert result["status"] == "COMPLETED_LOCAL_REVERSIBLE"
    assert result["outputs"]["text.stats"]["words"] == 3


def test_execute_selected_route():
    intent = IntentSpec.from_dict(demo_intent())
    catalog = manifests_from_iterable(demo_catalog())
    plan = select_route(intent, catalog)
    by_id = {cap.capability_id: cap for cap in catalog}
    result = execute_route([by_id[x] for x in plan["selected_route"]["capability_ids"]], intent.inputs)
    assert result["status"] == "COMPLETED_LOCAL_REVERSIBLE"
    assert "report.markdown" in result["outputs"]


def test_nonlocal_execution_stays_proposal_only():
    cap = manifests_from_iterable(demo_catalog())[0]
    result = execute_capability(cap, {"text.raw": "hello"})
    assert result["status"] == "PROPOSAL_ONLY_EXECUTOR_NOT_ACTIVE"
    assert result["external_action_authority"] == 0


def test_demo_writes_receipt_and_dashboard(tmp_path: Path):
    result = run_demo(tmp_path)
    assert Path(result["receipt"]).exists()
    assert Path(result["dashboard"]).exists()
    assert result["ledger"]["valid"]
