from __future__ import annotations

from pathlib import Path
from typing import Any

from .dashboard import generate_dashboard
from .executor import execute_route
from .ledger import append_event, verify_ledger
from .models import IntentSpec, manifests_from_iterable
from .planner import select_route
from .receipt import create_receipt
from .util import write_json


SAMPLE_TEXT = """New frontier models can choose among direct reasoning, generated code, APIs, browsers, and graphical interfaces. The important design question is no longer which application the user opens first. It is which capability route can satisfy the user's purpose with the lowest verified total expenditure while preserving authority, quality, privacy, and correction. A cheap route that fails and must be repeated may consume more energy and attention than a more reliable route. A function borrowed from another device or purchased from a provider must carry explicit terms, scope, expiry, provenance, and an outcome receipt. Interface access never creates new permission. A model may compress a repeated tool sequence into a reusable recipe, but that procedural internalization does not copy legal rights, proprietary code, or human authorization."""


def demo_catalog() -> list[dict[str, Any]]:
    return [
        {
            "capability_id": "model-native-full-brief",
            "name": "Model-native full brief",
            "description": "A frontier model produces the full brief without a separate application.",
            "provider_id": "model-provider",
            "owner_realm": "local-owner",
            "surface": "model_native",
            "requires": ["text.raw"],
            "provides": ["report.markdown"],
            "quality": 0.84,
            "authority_scopes": ["data.read"],
            "side_effect": "none",
            "cost": {"energy_j": 900, "verification_energy_j": 120, "coordination_energy_j": 20, "retry_energy_j": 1100, "latency_ms": 12000, "money": 0.05, "human_minutes": 6, "data_exposure": 0.25, "carbon_g": 0.12, "semantic_loss": 0.18, "failure_probability": 0.18, "measurement_source": "declared"},
            "executor": {"kind": "provider_required"},
        },
        {
            "capability_id": "local-text-stats",
            "name": "Local text statistics",
            "description": "Deterministic local text profiling.",
            "provider_id": "local-core",
            "owner_realm": "local-owner",
            "surface": "local_code",
            "requires": ["text.raw"],
            "provides": ["text.stats"],
            "quality": 0.999,
            "authority_scopes": ["data.read"],
            "side_effect": "none",
            "deterministic": True,
            "cacheable": True,
            "cost": {"energy_j": 2, "verification_energy_j": 0.5, "coordination_energy_j": 0.2, "retry_energy_j": 2, "latency_ms": 70, "money": 0, "human_minutes": 0, "data_exposure": 0, "carbon_g": 0.0003, "semantic_loss": 0, "failure_probability": 0.003, "measurement_source": "declared"},
            "executor": {"kind": "builtin", "handler": "text_stats"},
        },
        {
            "capability_id": "local-extractive-summary",
            "name": "Local extractive summary",
            "description": "A deterministic, source-preserving summary step.",
            "provider_id": "local-core",
            "owner_realm": "local-owner",
            "surface": "local_code",
            "requires": ["text.raw"],
            "provides": ["text.summary"],
            "quality": 0.93,
            "authority_scopes": ["data.read"],
            "side_effect": "none",
            "deterministic": True,
            "cacheable": True,
            "cost": {"energy_j": 6, "verification_energy_j": 1, "coordination_energy_j": 0.5, "retry_energy_j": 5, "latency_ms": 180, "money": 0, "human_minutes": 0.2, "data_exposure": 0, "carbon_g": 0.001, "semantic_loss": 0.06, "failure_probability": 0.01, "measurement_source": "declared"},
            "executor": {"kind": "builtin", "handler": "extractive_summary", "options": {"sentences": 5}},
        },
        {
            "capability_id": "local-markdown-compose",
            "name": "Local Markdown composition",
            "description": "Build a structured brief from verified local outputs.",
            "provider_id": "local-core",
            "owner_realm": "local-owner",
            "surface": "local_code",
            "requires": ["text.stats", "text.summary"],
            "provides": ["report.markdown"],
            "quality": 0.99,
            "authority_scopes": ["data.read"],
            "side_effect": "reversible_local",
            "deterministic": True,
            "cacheable": True,
            "cost": {"energy_j": 3, "verification_energy_j": 1, "coordination_energy_j": 0.4, "retry_energy_j": 3, "latency_ms": 100, "money": 0, "human_minutes": 0, "data_exposure": 0, "carbon_g": 0.0005, "semantic_loss": 0.01, "failure_probability": 0.005, "measurement_source": "declared"},
            "executor": {"kind": "builtin", "handler": "compose_markdown", "options": {"title": "MINEX Model-First Capability Brief"}},
        },
        {
            "capability_id": "local-api-brief",
            "name": "Local application API brief",
            "description": "Use a formal API exposed by an installed application.",
            "provider_id": "local-app",
            "owner_realm": "local-owner",
            "surface": "local_api",
            "requires": ["text.raw"],
            "provides": ["report.markdown"],
            "quality": 0.95,
            "authority_scopes": ["data.read", "app.invoke"],
            "side_effect": "reversible_local",
            "cost": {"energy_j": 35, "verification_energy_j": 8, "coordination_energy_j": 3, "retry_energy_j": 40, "latency_ms": 800, "money": 0.01, "human_minutes": 0.5, "data_exposure": 0.05, "carbon_g": 0.006, "semantic_loss": 0.03, "failure_probability": 0.025, "measurement_source": "declared"},
            "executor": {"kind": "adapter_required"},
        },
        {
            "capability_id": "legacy-gui-brief",
            "name": "Legacy GUI automation",
            "description": "Operate an installed application through its human interface.",
            "provider_id": "legacy-app",
            "owner_realm": "local-owner",
            "surface": "local_gui",
            "requires": ["text.raw"],
            "provides": ["report.markdown"],
            "quality": 0.91,
            "authority_scopes": ["data.read", "gui.control"],
            "side_effect": "reversible_local",
            "cost": {"energy_j": 520, "verification_energy_j": 90, "coordination_energy_j": 40, "retry_energy_j": 600, "latency_ms": 90000, "money": 0, "human_minutes": 3, "data_exposure": 0.02, "carbon_g": 0.09, "semantic_loss": 0.04, "failure_probability": 0.12, "measurement_source": "declared"},
            "executor": {"kind": "gui_adapter_required"},
        },
        {
            "capability_id": "peer-verified-summary",
            "name": "Same-owner peer summary",
            "description": "Borrow a summary capability from another authorized computer in the same owner realm.",
            "provider_id": "peer-node-02",
            "owner_realm": "local-owner",
            "surface": "same_owner_peer",
            "requires": ["text.raw"],
            "provides": ["text.summary"],
            "quality": 0.96,
            "authority_scopes": ["data.read", "peer.invoke"],
            "side_effect": "reversible_external",
            "cost": {"energy_j": 18, "verification_energy_j": 3, "coordination_energy_j": 4, "retry_energy_j": 20, "latency_ms": 450, "money": 0, "human_minutes": 0, "data_exposure": 0.18, "carbon_g": 0.004, "semantic_loss": 0.025, "failure_probability": 0.025, "measurement_source": "provider-declared"},
            "executor": {"kind": "peer_required"},
            "terms": {"lease_ttl_seconds": 900, "same_owner_only": True},
        },
        {
            "capability_id": "market-certified-brief",
            "name": "Paid verified briefing service",
            "description": "Purchase a high-confidence brief from a third-party capability provider.",
            "provider_id": "market-provider-17",
            "owner_realm": "external-provider",
            "surface": "market_service",
            "requires": ["text.raw"],
            "provides": ["report.markdown"],
            "quality": 0.985,
            "authority_scopes": ["data.read", "market.purchase"],
            "side_effect": "reversible_external",
            "cost": {"energy_j": 80, "verification_energy_j": 20, "coordination_energy_j": 12, "retry_energy_j": 100, "latency_ms": 4500, "money": 0.65, "human_minutes": 1, "data_exposure": 0.45, "carbon_g": 0.02, "semantic_loss": 0.015, "failure_probability": 0.01, "measurement_source": "provider-declared"},
            "executor": {"kind": "market_provider_required"},
            "terms": {"currency": "USD", "refund_on_verified_failure": True},
        },
        {
            "capability_id": "human-domain-editor",
            "name": "Human domain editor",
            "description": "Delegate the brief to a named human expert.",
            "provider_id": "human-review-network",
            "owner_realm": "external-provider",
            "surface": "human_delegate",
            "requires": ["text.raw"],
            "provides": ["report.markdown"],
            "quality": 0.99,
            "authority_scopes": ["data.read", "human.delegate"],
            "side_effect": "reversible_external",
            "cost": {"energy_j": 0, "verification_energy_j": 0, "coordination_energy_j": 5, "retry_energy_j": 0, "latency_ms": 1800000, "money": 25, "human_minutes": 30, "data_exposure": 0.5, "carbon_g": 0, "semantic_loss": 0.01, "failure_probability": 0.02, "measurement_source": "not-physically-measured"},
            "executor": {"kind": "human_required"},
        },
    ]


def demo_intent() -> dict[str, Any]:
    return {
        "intent_id": "intent-model-first-brief",
        "title": "Create a verified model-first capability brief",
        "purpose": "Produce a concise, traceable briefing while minimizing verified execution expenditure.",
        "available_types": ["text.raw"],
        "required_types": ["report.markdown"],
        "inputs": {"text.raw": SAMPLE_TEXT},
        "granted_scopes": ["data.read", "app.invoke"],
        "owner_realm": "local-owner",
        "currency": "USD",
        "constraints": {
            "allowed_surfaces": ["model_native", "local_code", "local_api", "local_gui", "same_owner_peer", "market_service", "human_delegate", "recipe"],
            "network_allowed": False,
            "external_purchase_allowed": False,
            "max_side_effect": "reversible_local",
            "max_expected_energy_j": 1500,
            "max_latency_ms": 120000,
            "max_money": 1.0,
            "max_human_minutes": 10,
            "max_data_exposure": 0.25,
            "max_semantic_loss": 0.20,
            "max_failure_probability": 0.20,
            "min_quality": 0.82,
            "normalization_references": {"expected_energy_j": 1000, "latency_ms": 60000, "money": 1, "human_minutes": 15, "data_exposure": 0.5, "carbon_g": 0.1, "semantic_loss": 0.2, "failure_probability": 0.2},
        },
        "weights": {"expected_energy_j": 0.35, "latency_ms": 0.12, "money": 0.08, "human_minutes": 0.10, "data_exposure": 0.12, "carbon_g": 0.06, "semantic_loss": 0.09, "failure_probability": 0.08},
    }


def run_demo(workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    catalog_dicts = demo_catalog()
    intent_dict = demo_intent()
    catalog = manifests_from_iterable(catalog_dicts)
    intent = IntentSpec.from_dict(intent_dict)
    write_json(workspace / "catalog.json", {"capabilities": catalog_dicts})
    write_json(workspace / "intent.json", intent_dict)
    plan = select_route(intent, catalog)
    write_json(workspace / "plan.json", plan)
    execution = None
    selected = plan.get("selected_route")
    if selected:
        by_id = {cap.capability_id: cap for cap in catalog}
        caps = [by_id[item] for item in selected["capability_ids"]]
        execution = execute_route(caps, intent.inputs, catalog_map=by_id)
        write_json(workspace / "execution.json", execution)
    receipt_path, receipt = create_receipt(workspace, intent.to_dict(), plan, execution)
    dashboard_path = generate_dashboard(plan, workspace / "dashboard.html")
    append_event(workspace / "responsibility-ledger.jsonl", "demo.completed", {
        "selected_route": selected["route_id"] if selected else None,
        "receipt_digest": receipt["receipt_digest"],
    })
    ledger = verify_ledger(workspace / "responsibility-ledger.jsonl")
    result = {
        "workspace": str(workspace),
        "selected_route": selected,
        "execution_status": execution.get("status") if execution else "NO_ROUTE",
        "receipt": str(receipt_path),
        "dashboard": str(dashboard_path),
        "ledger": ledger,
        "automatic_external_action_authority": 0,
    }
    write_json(workspace / "demo-result.json", result)
    return result
