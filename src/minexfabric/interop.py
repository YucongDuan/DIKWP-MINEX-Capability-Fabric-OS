from __future__ import annotations

from typing import Any


def mcp_tool_descriptions() -> list[dict[str, Any]]:
    return [
        {
            "name": "minex_plan_intent",
            "description": "Plan a Pareto-efficient, authority-bounded capability route for an intent.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "intent": {"type": "object"},
                    "catalog": {"type": "array", "items": {"type": "object"}},
                    "max_steps": {"type": "integer", "minimum": 1, "maximum": 12, "default": 6},
                },
                "required": ["intent", "catalog"],
            },
        },
        {
            "name": "minex_compare_routes",
            "description": "Return the Pareto frontier and explain rejected routes without executing them.",
            "inputSchema": {
                "type": "object",
                "properties": {"intent": {"type": "object"}, "catalog": {"type": "array", "items": {"type": "object"}}},
                "required": ["intent", "catalog"],
            },
        },
        {
            "name": "minex_verify_ledger",
            "description": "Verify an append-only MINEX responsibility ledger.",
            "inputSchema": {
                "type": "object",
                "properties": {"ledger_jsonl": {"type": "string", "maxLength": 2000000}},
                "required": ["ledger_jsonl"],
            },
        },
    ]


def a2a_agent_card() -> dict[str, Any]:
    return {
        "name": "DIKWP MINEX Capability Fabric",
        "description": "Plans minimum verified execution-expenditure routes across model-native, code, API, GUI, trusted peer, market, and human capabilities.",
        "version": "1.0.0",
        "protocolVersion": "1.0",
        "capabilities": {"streaming": False, "pushNotifications": False, "stateTransitionHistory": True},
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/markdown"],
        "skills": [
            {
                "id": "plan-capability-route",
                "name": "Plan capability route",
                "description": "Build a Pareto frontier under authority, quality, privacy, energy, time, and cost constraints.",
                "tags": ["routing", "capabilities", "energy", "MCP", "A2A", "DIKWP"],
                "examples": ["Choose whether to reason directly, run code, call an API, use a GUI, borrow a peer function, or buy a service."],
            }
        ],
        "securitySchemes": {},
        "security": [],
        "extensions": [
            {"uri": "https://github.com/YucongDuan/DIKWP-MINEX-Capability-Fabric-OS#authority-boundary", "description": "Reference implementation has no automatic external action authority.", "required": True}
        ],
    }


def openapi_spec() -> dict[str, Any]:
    return {
        "openapi": "3.1.1",
        "info": {"title": "DIKWP MINEX Local API", "version": "1.0.0"},
        "servers": [{"url": "http://127.0.0.1:8765"}],
        "paths": {
            "/health": {"get": {"responses": {"200": {"description": "Health"}}}},
            "/v1/plan": {
                "post": {
                    "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}},
                    "responses": {"200": {"description": "Capability route plan"}},
                }
            },
        },
    }
