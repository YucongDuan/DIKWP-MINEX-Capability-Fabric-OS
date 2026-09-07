from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .api import serve as serve_api
from .catalog import catalog_to_dict, load_catalog
from .dashboard import generate_dashboard
from .demo import run_demo
from .distill import distill_receipt
from .executor import execute_route
from .interop import a2a_agent_card, mcp_tool_descriptions, openapi_spec
from .lease import create_lease, verify_lease
from .ledger import verify_ledger
from .market import clear_market, settlement_proposal
from .mcp import serve as serve_mcp
from .models import IntentSpec
from .peer import serve_peer
from .planner import select_route
from .receipt import create_receipt
from .util import MinExError, read_json, write_json


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _emit(value: Any, output: str | None = None) -> None:
    if output:
        write_json(_path(output), value)
    else:
        print(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="minex", description="Route intents across model, code, API, GUI, peer, market, and human capabilities by minimum verified execution expenditure.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("plan", help="Plan an authority-bounded Pareto route.")
    p.add_argument("intent")
    p.add_argument("catalog")
    p.add_argument("--max-steps", type=int, default=6)
    p.add_argument("--output")

    p = sub.add_parser("execute", help="Execute a selected route when every step is a safe local builtin.")
    p.add_argument("intent")
    p.add_argument("catalog")
    p.add_argument("--workspace", default=".minex-run")
    p.add_argument("--max-steps", type=int, default=6)

    p = sub.add_parser("catalog", help="Normalize and inspect a capability catalog.")
    p.add_argument("catalog")
    p.add_argument("--output")

    p = sub.add_parser("demo", help="Run the complete local demonstration.")
    p.add_argument("--workspace", default=".minex-demo")
    p.add_argument("--reset", action="store_true")

    p = sub.add_parser("dashboard", help="Generate a self-contained route dashboard from a plan JSON.")
    p.add_argument("plan")
    p.add_argument("--output", default="minex-dashboard.html")

    p = sub.add_parser("distill", help="Distill a verified local route into a reusable recipe manifest.")
    p.add_argument("receipt")
    p.add_argument("--id", required=True)
    p.add_argument("--name")
    p.add_argument("--output", required=True)

    p = sub.add_parser("lease-create", help="Create a bounded HMAC capability lease.")
    p.add_argument("--capability", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--consumer", required=True)
    p.add_argument("--secret-file", required=True)
    p.add_argument("--owner-realm", default="local-owner")
    p.add_argument("--ttl", type=int, default=900)
    p.add_argument("--max-calls", type=int, default=1)
    p.add_argument("--max-money", type=float, default=0.0)
    p.add_argument("--output")

    p = sub.add_parser("lease-verify", help="Verify a bounded HMAC capability lease.")
    p.add_argument("lease")
    p.add_argument("--secret-file", required=True)
    p.add_argument("--capability")

    p = sub.add_parser("market-clear", help="Clear a simulated capability market.")
    p.add_argument("bids")
    p.add_argument("--requirement", required=True)
    p.add_argument("--max-money", type=float, required=True)
    p.add_argument("--owner-realm", default="local-owner")
    p.add_argument("--output")

    p = sub.add_parser("settlement-proposal", help="Create a no-payment settlement proposal from a winning bid and receipt.")
    p.add_argument("bid")
    p.add_argument("--receipt-digest", required=True)
    p.add_argument("--output")

    p = sub.add_parser("serve", help="Run the loopback-only local planning API.")
    p.add_argument("catalog")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--allow-nonloopback", action="store_true")

    p = sub.add_parser("peer-serve", help="Serve safe builtin capabilities to an authorized peer.")
    p.add_argument("catalog")
    p.add_argument("--secret-file", required=True)
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--allow-nonloopback", action="store_true")

    sub.add_parser("mcp", help="Run the stateless local MCP stdio server.")

    p = sub.add_parser("interop", help="Export MCP, A2A, or OpenAPI reference descriptions.")
    p.add_argument("kind", choices=["mcp", "a2a", "openapi"])
    p.add_argument("--output")

    p = sub.add_parser("verify-ledger", help="Verify a MINEX responsibility ledger.")
    p.add_argument("path")

    return parser


def run(args: argparse.Namespace) -> int:
    if args.command == "plan":
        result = select_route(IntentSpec.from_dict(read_json(_path(args.intent))), load_catalog(_path(args.catalog)), max_steps=args.max_steps)
        _emit(result, args.output)
        return 0 if result.get("selected_route") else 2
    if args.command == "execute":
        workspace = _path(args.workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        intent = IntentSpec.from_dict(read_json(_path(args.intent)))
        catalog = load_catalog(_path(args.catalog))
        plan = select_route(intent, catalog, max_steps=args.max_steps)
        by_id = {cap.capability_id: cap for cap in catalog}
        selected = plan.get("selected_route")
        execution = None
        if selected:
            execution = execute_route([by_id[item] for item in selected["capability_ids"]], intent.inputs, catalog_map=by_id)
        write_json(workspace / "plan.json", plan)
        if execution is not None:
            write_json(workspace / "execution.json", execution)
        receipt_path, receipt = create_receipt(workspace, intent.to_dict(), plan, execution)
        result = {"plan": plan, "execution": execution, "receipt": str(receipt_path), "receipt_digest": receipt["receipt_digest"]}
        _emit(result)
        return 0 if execution and execution.get("status") == "COMPLETED_LOCAL_REVERSIBLE" else 3
    if args.command == "catalog":
        _emit(catalog_to_dict(load_catalog(_path(args.catalog))), args.output)
        return 0
    if args.command == "demo":
        workspace = _path(args.workspace)
        if args.reset and workspace.exists():
            import shutil
            shutil.rmtree(workspace)
        _emit(run_demo(workspace))
        return 0
    if args.command == "dashboard":
        print(generate_dashboard(read_json(_path(args.plan)), _path(args.output)))
        return 0
    if args.command == "distill":
        manifest = distill_receipt(read_json(_path(args.receipt)), args.id, args.name)
        write_json(_path(args.output), manifest)
        _emit(manifest)
        return 0
    if args.command == "lease-create":
        secret = _path(args.secret_file).read_bytes().strip()
        result = create_lease(args.capability, args.provider, args.consumer, secret, max_calls=args.max_calls, max_money=args.max_money, ttl_seconds=args.ttl, owner_realm=args.owner_realm)
        _emit(result, args.output)
        return 0
    if args.command == "lease-verify":
        result = verify_lease(read_json(_path(args.lease)), _path(args.secret_file).read_bytes().strip(), args.capability)
        _emit(result)
        return 0 if result["valid"] else 1
    if args.command == "market-clear":
        data = read_json(_path(args.bids))
        bids = data.get("bids", data) if isinstance(data, dict) else data
        result = clear_market(args.requirement, bids, args.max_money, args.owner_realm)
        _emit(result, args.output)
        return 0 if result["winner"] else 2
    if args.command == "settlement-proposal":
        _emit(settlement_proposal(read_json(_path(args.bid)), args.receipt_digest), args.output)
        return 0
    if args.command == "serve":
        return serve_api(_path(args.catalog), args.host, args.port, args.allow_nonloopback)
    if args.command == "peer-serve":
        return serve_peer(_path(args.catalog), _path(args.secret_file), args.host, args.port, args.allow_nonloopback)
    if args.command == "mcp":
        return serve_mcp()
    if args.command == "interop":
        value = {"mcp": {"protocolVersion": "2026-07-28", "tools": mcp_tool_descriptions()}, "a2a": a2a_agent_card(), "openapi": openapi_spec()}[args.kind]
        _emit(value, args.output)
        return 0
    if args.command == "verify-ledger":
        result = verify_ledger(_path(args.path))
        _emit(result)
        return 0 if result["valid"] else 1
    raise MinExError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        return run(parser.parse_args(argv))
    except MinExError as exc:
        print(f"minex: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
