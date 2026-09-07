from pathlib import Path

from minexfabric.interop import a2a_agent_card, mcp_tool_descriptions, openapi_spec
from minexfabric.ledger import append_event, verify_ledger
from minexfabric.mcp import handle


def test_ledger_tamper_detection(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_event(path, "one", {"x": 1})
    append_event(path, "two", {"x": 2})
    assert verify_ledger(path)["valid"]
    text = path.read_text(encoding="utf-8").replace('"x":2', '"x":3')
    path.write_text(text, encoding="utf-8")
    assert not verify_ledger(path)["valid"]


def test_openapi_loopback_server():
    spec = openapi_spec()
    assert spec["openapi"] == "3.1.1"
    assert spec["servers"][0]["url"].startswith("http://127.0.0.1")


def test_a2a_has_skill_and_zero_authority_extension():
    card = a2a_agent_card()
    assert card["protocolVersion"] == "1.0"
    assert card["skills"]
    assert card["extensions"][0]["required"]


def test_mcp_initialize_and_tools():
    init = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert init["result"]["protocolVersion"] == "2026-07-28"
    tools = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    assert len(tools["result"]["tools"]) == len(mcp_tool_descriptions())


def test_mcp_ledger_verification_uses_content_not_arbitrary_path(tmp_path: Path):
    from minexfabric.ledger import append_event
    from minexfabric.mcp import handle

    path = tmp_path / "ledger.jsonl"
    append_event(path, "demo", {"x": 1})
    response = handle({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "minex_verify_ledger",
            "arguments": {"ledger_jsonl": path.read_text(encoding="utf-8")},
        },
    })
    assert response is not None
    assert response["result"]["structuredContent"]["valid"] is True
