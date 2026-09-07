from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from .util import MinExError, clamp, finite_nonnegative, sha256_json


def _normalize_bid(raw: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    reasons: list[str] = []
    try:
        bid = dict(raw)
        bid["capability_id"] = str(bid["capability_id"])
        bid["provider_id"] = str(bid["provider_id"])
        bid["provides"] = sorted({str(x) for x in bid.get("provides", [])})
        bid["money"] = finite_nonnegative(bid.get("money", 0.0), "bid.money")
        bid["expected_energy_j"] = finite_nonnegative(bid.get("expected_energy_j", 0.0), "bid.expected_energy_j")
        bid["quality"] = clamp(float(bid.get("quality", 0.0)))
        bid["currency"] = str(bid.get("currency", "USD")).upper()[:12]
        bid["available"] = bool(bid.get("available", True))
        bid["same_owner_only"] = bool(bid.get("same_owner_only", False))
        bid["owner_realm"] = str(bid.get("owner_realm", ""))
        if not bid["capability_id"] or not bid["provider_id"]:
            reasons.append("MISSING_IDENTITY")
    except (KeyError, TypeError, ValueError, MinExError) as exc:
        return None, [f"INVALID_BID:{type(exc).__name__}"]
    return bid, reasons


def clear_market(requirement: str, bids: Iterable[dict[str, Any]], max_money: float, owner_realm: str) -> dict[str, Any]:
    budget = finite_nonnegative(max_money, "max_money")
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for raw in bids:
        bid, reasons = _normalize_bid(raw)
        if bid is None:
            rejected.append({"bid": raw, "reasons": reasons})
            continue
        if requirement not in set(bid.get("provides", [])):
            reasons.append("OUTPUT_NOT_PROVIDED")
        if bid["money"] > budget:
            reasons.append("PRICE_EXCEEDS_BUDGET")
        if not bid["available"]:
            reasons.append("BID_UNAVAILABLE")
        if bid["same_owner_only"] and bid["owner_realm"] != owner_realm:
            reasons.append("OWNER_REALM_MISMATCH")
        row = {"bid": bid, "reasons": sorted(set(reasons))}
        (rejected if reasons else eligible).append(row)
    eligible.sort(key=lambda row: (
        float(row["bid"]["money"]),
        float(row["bid"]["expected_energy_j"]),
        -float(row["bid"]["quality"]),
        str(row["bid"]["provider_id"]),
    ))
    winner = eligible[0]["bid"] if eligible else None
    return {
        "clearing_id": "clear-" + sha256_json({"requirement": requirement, "winner": winner, "time": datetime.now(timezone.utc).isoformat()})[:20],
        "requirement": requirement,
        "winner": winner,
        "eligible": [row["bid"] for row in eligible],
        "rejected": rejected,
        "settlement_status": "PROPOSAL_ONLY_NO_REAL_PAYMENT",
        "automatic_payment_authority": 0,
    }


def settlement_proposal(bid: dict[str, Any], receipt_digest: str) -> dict[str, Any]:
    normalized, reasons = _normalize_bid(bid)
    if normalized is None or reasons:
        raise ValueError(f"Invalid winning bid: {','.join(reasons)}")
    if not receipt_digest or len(receipt_digest) > 256:
        raise ValueError("receipt_digest is required and must be bounded")
    proposal = {
        "type": "MINEX_MARKET_SETTLEMENT_PROPOSAL",
        "provider_id": normalized["provider_id"],
        "capability_id": normalized["capability_id"],
        "amount": normalized["money"],
        "currency": normalized["currency"],
        "receipt_digest": receipt_digest,
        "status": "PROPOSAL_ONLY_NO_REAL_PAYMENT",
        "automatic_payment_authority": 0,
    }
    proposal["proposal_digest"] = sha256_json(proposal)
    return proposal
