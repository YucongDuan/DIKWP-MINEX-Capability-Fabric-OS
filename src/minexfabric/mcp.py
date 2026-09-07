from __future__ import annotations

import json
import sys
from typing import Any

from .ledger import verify_ledger_text
from .interop import mcp_tool_descriptions
from .models import IntentSpec, manifests_from_iterable
from .planner import select_route

PROTOCOL_VERSION = "2026-07-28"


def _response(request_id: Any, result: Any = None, error: Any = None) -> dict[str, Any]:
    data: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        data["error"] = error
    else:
        data["result"] = result
    return data


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _response(request_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "dikwp-minex", "version": "1.0.0"},
            "instructions": "Plans authority-bounded capability routes. It does not execute external actions or payments.",
        })
    if method == "tools/list":
        return _response(request_id, {"tools": mcp_tool_descriptions()})
    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        try:
            if name in {"minex_plan_intent", "minex_compare_routes"}:
                catalog = list(args["catalog"])
                if len(catalog) > 512:
                    raise ValueError("catalog exceeds 512 capability limit")
                result = select_route(
                    IntentSpec.from_dict(args["intent"]),
                    manifests_from_iterable(catalog),
                    max_steps=max(1, min(12, int(args.get("max_steps", 6)))),
                )
            elif name == "minex_verify_ledger":
                ledger_jsonl = str(args["ledger_jsonl"])
                if len(ledger_jsonl.encode("utf-8")) > 2_000_000:
                    raise ValueError("ledger_jsonl exceeds 2 MB MCP limit")
                result = verify_ledger_text(ledger_jsonl)
            else:
                return _response(request_id, error={"code": -32602, "message": f"Unknown tool: {name}"})
            return _response(request_id, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}], "structuredContent": result})
        except Exception as exc:
            return _response(request_id, error={"code": -32000, "message": str(exc)})
    if request_id is not None:
        return _response(request_id, error={"code": -32601, "message": f"Method not found: {method}"})
    return None


def serve() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        if len(line.encode("utf-8")) > 2_000_000:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "request exceeds 2 MB limit"}}) + "\n")
            sys.stdout.flush()
            continue
        try:
            message = json.loads(line)
            response = handle(message)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}) + "\n")
            sys.stdout.flush()
    return 0
