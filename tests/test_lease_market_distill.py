from pathlib import Path

from minexfabric.demo import run_demo
from minexfabric.distill import distill_receipt
from minexfabric.lease import create_lease, verify_lease
from minexfabric.market import clear_market, settlement_proposal
from minexfabric.util import read_json


def test_lease_roundtrip():
    secret = b"a sufficiently long shared secret"
    lease = create_lease("cap-1", "provider", "consumer", secret)
    assert verify_lease(lease, secret, "cap-1")["valid"]


def test_lease_rejects_wrong_secret():
    lease = create_lease("cap-1", "provider", "consumer", b"correct secret long enough")
    assert not verify_lease(lease, b"wrong secret but still long", "cap-1")["valid"]


def test_market_chooses_lowest_price_then_energy():
    bids = [
        {"capability_id": "a", "provider_id": "p1", "provides": ["x"], "money": 1.0, "expected_energy_j": 10, "quality": 0.9},
        {"capability_id": "b", "provider_id": "p2", "provides": ["x"], "money": 0.5, "expected_energy_j": 50, "quality": 0.95},
    ]
    result = clear_market("x", bids, 2.0, "local-owner")
    assert result["winner"]["capability_id"] == "b"
    assert result["automatic_payment_authority"] == 0


def test_settlement_is_proposal_only():
    proposal = settlement_proposal({"capability_id": "a", "provider_id": "p", "money": 2, "currency": "USD"}, "abc")
    assert proposal["status"] == "PROPOSAL_ONLY_NO_REAL_PAYMENT"


def test_distill_verified_demo(tmp_path: Path):
    result = run_demo(tmp_path)
    receipt = read_json(Path(result["receipt"]))
    manifest = distill_receipt(receipt, "distilled-brief")
    assert manifest["surface"] == "recipe"
    assert manifest["terms"]["external_action_authority"] == 0


def test_lease_binds_consumer_owner_and_provider():
    secret = b"a sufficiently long shared secret"
    lease = create_lease("cap-1", "provider", "consumer", secret, owner_realm="realm-a")
    assert verify_lease(
        lease,
        secret,
        "cap-1",
        expected_provider_id="provider",
        expected_consumer_id="consumer",
        expected_owner_realm="realm-a",
    )["valid"]
    rejected = verify_lease(lease, secret, "cap-1", expected_consumer_id="other")
    assert "CONSUMER_MISMATCH" in rejected["reasons"]


def test_market_rejects_nonfinite_bid():
    bids = [{"capability_id": "bad", "provider_id": "p", "provides": ["x"], "money": float("nan")}]
    result = clear_market("x", bids, 2.0, "local-owner")
    assert result["winner"] is None
    assert result["rejected"]


def test_distilled_demo_is_deterministic(tmp_path: Path):
    result = run_demo(tmp_path)
    receipt = read_json(Path(result["receipt"]))
    manifest = distill_receipt(receipt, "distilled-deterministic-brief")
    assert manifest["deterministic"] is True
