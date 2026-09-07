from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "minexfabric"
FORBIDDEN_CALLS = {"eval", "exec", "compile", "os.system", "subprocess.run", "subprocess.Popen", "subprocess.call", "pickle.loads", "marshal.loads"}
NETWORK_MODULES = {"socket", "requests", "httpx", "aiohttp"}
ALLOWED_NETWORK_FILES = {"api.py", "peer.py"}


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return dotted(node.value) + "." + node.attr
    return ""


def main() -> int:
    findings = []
    scanned = 0
    for path in sorted(SRC.glob("*.py")):
        scanned += 1
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = dotted(node.func)
                if name in FORBIDDEN_CALLS:
                    findings.append({"file": path.name, "line": node.lineno, "finding": f"forbidden_call:{name}"})
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name.split(".")[0] for alias in node.names] if isinstance(node, ast.Import) else [(node.module or "").split(".")[0]]
                for name in names:
                    if name in NETWORK_MODULES and path.name not in ALLOWED_NETWORK_FILES:
                        findings.append({"file": path.name, "line": node.lineno, "finding": f"unexpected_network_module:{name}"})
    receipt = {
        "audit": "MINEX_STATIC_AUDIT",
        "python_modules_scanned": scanned,
        "findings": findings,
        "passed": not findings,
        "notes": [
            "api.py and peer.py intentionally use Python's local HTTP server. Non-loopback binding requires an explicit flag.",
            "The audit is a narrow static check, not a security certification.",
        ],
    }
    out = ROOT / "validation" / "STATIC_AUDIT_RECEIPT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
