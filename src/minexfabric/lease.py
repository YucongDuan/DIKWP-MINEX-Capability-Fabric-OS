from __future__ import annotations

import hashlib
import hmac
import math
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from .util import canonical_json, sha256_json


def create_lease(
    capability_id: str,
    provider_id: str,
    consumer_id: str,
    secret: bytes,
    *,
    max_calls: int = 1,
    max_money: float = 0.0,
    ttl_seconds: int = 900,
    owner_realm: str = "local-owner",
) -> dict[str, Any]:
    if len(secret) < 16:
        raise ValueError("Lease secret must be at least 16 bytes")
    money = float(max_money)
    if not math.isfinite(money) or money < 0:
        raise ValueError("max_money must be finite and non-negative")
    now = datetime.now(timezone.utc)
    nonce = secrets.token_hex(12)
    lease = {
        "lease_id": "lease-" + sha256_json({
            "capability_id": capability_id,
            "consumer_id": consumer_id,
            "issued_at": now.isoformat(),
            "nonce": nonce,
        })[:20],
        "capability_id": capability_id,
        "provider_id": provider_id,
        "consumer_id": consumer_id,
        "owner_realm": owner_realm,
        "nonce": nonce,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=max(1, min(int(ttl_seconds), 86_400)))).isoformat(),
        "max_calls": max(1, min(int(max_calls), 10_000)),
        "calls_used": 0,
        "max_money": money,
        "external_action_authority": 0,
    }
    lease["signature"] = hmac.new(secret, canonical_json(lease).encode("utf-8"), hashlib.sha256).hexdigest()
    return lease


def verify_lease(
    lease: dict[str, Any],
    secret: bytes,
    expected_capability_id: str | None = None,
    *,
    expected_provider_id: str | None = None,
    expected_consumer_id: str | None = None,
    expected_owner_realm: str | None = None,
    calls_used_override: int | None = None,
) -> dict[str, Any]:
    candidate = dict(lease)
    signature = str(candidate.pop("signature", ""))
    expected = hmac.new(secret, canonical_json(candidate).encode("utf-8"), hashlib.sha256).hexdigest()
    reasons: list[str] = []
    if not hmac.compare_digest(signature, expected):
        reasons.append("INVALID_SIGNATURE")
    try:
        expires = datetime.fromisoformat(str(candidate["expires_at"]))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) >= expires:
            reasons.append("LEASE_EXPIRED")
    except (KeyError, ValueError):
        reasons.append("INVALID_EXPIRY")
    if expected_capability_id and candidate.get("capability_id") != expected_capability_id:
        reasons.append("CAPABILITY_MISMATCH")
    if expected_provider_id and candidate.get("provider_id") != expected_provider_id:
        reasons.append("PROVIDER_MISMATCH")
    if expected_consumer_id and candidate.get("consumer_id") != expected_consumer_id:
        reasons.append("CONSUMER_MISMATCH")
    if expected_owner_realm and candidate.get("owner_realm") != expected_owner_realm:
        reasons.append("OWNER_REALM_MISMATCH")
    used = int(candidate.get("calls_used", 0)) if calls_used_override is None else int(calls_used_override)
    if used >= int(candidate.get("max_calls", 0)):
        reasons.append("CALL_BUDGET_EXHAUSTED")
    try:
        money = float(candidate.get("max_money", 0.0))
        if not math.isfinite(money) or money < 0:
            reasons.append("INVALID_MONEY_BUDGET")
    except (TypeError, ValueError):
        reasons.append("INVALID_MONEY_BUDGET")
    if int(candidate.get("external_action_authority", 0)) != 0:
        reasons.append("EXTERNAL_AUTHORITY_MUST_BE_ZERO")
    return {
        "valid": not reasons,
        "reasons": sorted(set(reasons)),
        "lease_id": candidate.get("lease_id"),
        "max_calls": candidate.get("max_calls"),
        "calls_used": used,
    }
