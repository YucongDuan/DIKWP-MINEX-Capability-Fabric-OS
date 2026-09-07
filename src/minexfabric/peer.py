from __future__ import annotations

import hashlib
import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any

from .catalog import load_catalog
from .executor import execute_capability
from .lease import verify_lease
from .models import CapabilityManifest

MAX_BODY_BYTES = 1_048_576
MAX_REPLAY_IDS = 20_000


def _signature(secret: bytes, body: bytes) -> str:
    return hmac.new(secret, body, hashlib.sha256).hexdigest()


class PeerState:
    def __init__(self, catalog: list[CapabilityManifest], secret: bytes):
        self.catalog = {cap.capability_id: cap for cap in catalog}
        self.secret = secret
        self.lease_calls: dict[str, int] = {}
        self.seen_request_ids: set[str] = set()
        self.lock = Lock()

    def reserve_call(self, request_id: str, lease: dict[str, Any], cap: CapabilityManifest, consumer_id: str) -> dict[str, Any]:
        lease_id = str(lease.get("lease_id", ""))
        if not request_id or len(request_id) > 200:
            return {"valid": False, "reasons": ["INVALID_REQUEST_ID"]}
        if not lease_id:
            return {"valid": False, "reasons": ["MISSING_LEASE_ID"]}
        with self.lock:
            if request_id in self.seen_request_ids:
                return {"valid": False, "reasons": ["REPLAYED_REQUEST_ID"]}
            used = self.lease_calls.get(lease_id, 0)
            check = verify_lease(
                lease,
                self.secret,
                cap.capability_id,
                expected_provider_id=cap.provider_id,
                expected_consumer_id=consumer_id,
                expected_owner_realm=cap.owner_realm,
                calls_used_override=used,
            )
            if not check["valid"]:
                return check
            self.seen_request_ids.add(request_id)
            if len(self.seen_request_ids) > MAX_REPLAY_IDS:
                # Bounded memory: drop an arbitrary old identifier. Leases remain call-budget bounded.
                self.seen_request_ids.pop()
            self.lease_calls[lease_id] = used + 1
            return {**check, "calls_used_after": used + 1}


class Handler(BaseHTTPRequestHandler):
    server_version = "MINEXPeer/1.0"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    @property
    def state(self) -> PeerState:
        return self.server.state  # type: ignore[attr-defined]

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json(200, {"status": "ok", "external_action_authority": 0})
            return
        if self.path == "/v1/capabilities":
            expected = _signature(self.state.secret, b"GET\n/v1/capabilities")
            if not hmac.compare_digest(self.headers.get("X-MINEX-Signature", ""), expected):
                self._json(403, {"error": "invalid_request_signature"})
                return
            self._json(200, {"capabilities": [cap.to_dict() for cap in self.state.catalog.values()]})
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "invalid_content_length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._json(413 if length > MAX_BODY_BYTES else 400, {"error": "invalid_body_size", "max_bytes": MAX_BODY_BYTES})
            return
        body = self.rfile.read(length)
        signature = self.headers.get("X-MINEX-Signature", "")
        if not hmac.compare_digest(signature, _signature(self.state.secret, body)):
            self._json(403, {"error": "invalid_request_signature"})
            return
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._json(400, {"error": "invalid_json"})
            return
        if self.path != "/v1/execute":
            self._json(404, {"error": "not_found"})
            return
        capability_id = str(payload.get("capability_id", ""))
        cap = self.state.catalog.get(capability_id)
        if not cap:
            self._json(404, {"error": "capability_not_found"})
            return
        if cap.executor.get("kind") != "builtin":
            self._json(409, {"error": "peer_executes_builtin_only"})
            return
        inputs = dict(payload.get("inputs", {}))
        if any(str(key).endswith(".path") for key in inputs):
            self._json(403, {"error": "peer_file_path_inputs_prohibited"})
            return
        reservation = self.state.reserve_call(
            str(payload.get("request_id", "")),
            dict(payload.get("lease", {})),
            cap,
            str(payload.get("consumer_id", "")),
        )
        if not reservation.get("valid"):
            self._json(403, {"error": "invalid_lease_or_replay", "reasons": reservation.get("reasons", [])})
            return
        result = execute_capability(cap, inputs)
        result["lease_usage"] = {
            "lease_id": reservation.get("lease_id"),
            "calls_used_after": reservation.get("calls_used_after"),
            "max_calls": reservation.get("max_calls"),
        }
        self._json(200, result)


def serve_peer(catalog_path: Path, secret_file: Path, host: str = "127.0.0.1", port: int = 8766, allow_nonloopback: bool = False) -> int:
    if host not in {"127.0.0.1", "localhost", "::1"} and not allow_nonloopback:
        raise RuntimeError("Non-loopback peer binding requires --allow-nonloopback")
    secret = secret_file.read_bytes().strip()
    if len(secret) < 16:
        raise RuntimeError("Peer shared secret must be at least 16 bytes")
    server = ThreadingHTTPServer((host, port), Handler)
    server.state = PeerState(load_catalog(catalog_path), secret)  # type: ignore[attr-defined]
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0
