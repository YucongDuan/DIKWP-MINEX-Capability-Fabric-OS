from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .catalog import load_catalog
from .models import IntentSpec
from .planner import select_route

MAX_BODY_BYTES = 1_048_576


class APIState:
    def __init__(self, catalog_path: Path):
        self.catalog_path = catalog_path


class Handler(BaseHTTPRequestHandler):
    server_version = "MINEXLocalAPI/1.0"

    @property
    def state(self) -> APIState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "ok", "system": "DIKWP MINEX", "external_action_authority": 0})
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/v1/plan":
            self._send(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, {"error": "invalid_content_length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._send(413 if length > MAX_BODY_BYTES else 400, {"error": "invalid_body_size", "max_bytes": MAX_BODY_BYTES})
            return
        try:
            payload = json.loads(self.rfile.read(length))
            intent = IntentSpec.from_dict(payload.get("intent", payload))
            # The HTTP boundary never accepts a caller-controlled filesystem path.
            # A server operator chooses the catalog at process start.
            catalog_path = self.state.catalog_path
            max_steps = max(1, min(12, int(payload.get("max_steps", 6))))
            result = select_route(intent, load_catalog(catalog_path), max_steps=max_steps)
            self._send(200, result)
        except Exception as exc:  # boundary returns an explicit error
            self._send(400, {"error": type(exc).__name__, "message": str(exc)})


def serve(catalog_path: Path, host: str = "127.0.0.1", port: int = 8765, allow_nonloopback: bool = False) -> int:
    if host not in {"127.0.0.1", "localhost", "::1"} and not allow_nonloopback:
        raise RuntimeError("Non-loopback binding requires --allow-nonloopback")
    server = ThreadingHTTPServer((host, port), Handler)
    server.state = APIState(catalog_path)  # type: ignore[attr-defined]
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
