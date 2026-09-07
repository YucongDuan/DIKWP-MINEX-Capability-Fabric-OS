from minexfabric.executor import execute_route
from minexfabric.models import CapabilityManifest


def cap(data):
    return CapabilityManifest.from_dict(data)


def test_distilled_recipe_executes_registered_local_steps():
    stats = cap({
        "capability_id": "stats", "name": "stats", "provider_id": "local", "owner_realm": "r",
        "surface": "local_code", "requires": ["text.raw"], "provides": ["text.stats"],
        "quality": 0.99, "cost": {}, "executor": {"kind": "builtin", "handler": "text_stats"}
    })
    summary = cap({
        "capability_id": "summary", "name": "summary", "provider_id": "local", "owner_realm": "r",
        "surface": "local_code", "requires": ["text.raw"], "provides": ["text.summary"],
        "quality": 0.90, "cost": {}, "executor": {"kind": "builtin", "handler": "extractive_summary"}
    })
    compose = cap({
        "capability_id": "compose", "name": "compose", "provider_id": "local", "owner_realm": "r",
        "surface": "local_code", "requires": ["text.stats", "text.summary"], "provides": ["report.markdown"],
        "quality": 0.99, "cost": {}, "executor": {"kind": "builtin", "handler": "compose_markdown"}
    })
    recipe = cap({
        "capability_id": "recipe", "name": "recipe", "provider_id": "local", "owner_realm": "r",
        "surface": "recipe", "requires": ["text.raw"], "provides": ["report.markdown"],
        "quality": 0.88, "cost": {}, "executor": {"kind": "recipe", "steps": ["summary", "stats", "compose"]}
    })
    catalog = {x.capability_id: x for x in [stats, summary, compose, recipe]}
    result = execute_route([recipe], {"text.raw": "One sentence. Another sentence."}, catalog_map=catalog)
    assert result["status"] == "COMPLETED_LOCAL_REVERSIBLE"
    assert "report.markdown" in result["outputs"]
    assert result["external_action_authority"] == 0
