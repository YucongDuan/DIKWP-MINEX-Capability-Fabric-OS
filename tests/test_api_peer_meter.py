from pathlib import Path

import pytest

from minexfabric.api import serve
from minexfabric.meter import measure_call
from minexfabric.peer import serve_peer


def test_measure_call_returns_timings():
    result, measurement = measure_call(lambda: sum(range(100)))
    assert result == 4950
    assert measurement.wall_ms >= 0
    assert measurement.cpu_ms >= 0


def test_api_rejects_nonloopback_without_flag(tmp_path: Path):
    with pytest.raises(RuntimeError):
        serve(tmp_path / "catalog.json", "0.0.0.0", 0, False)


def test_peer_rejects_nonloopback_without_flag(tmp_path: Path):
    secret = tmp_path / "secret"
    secret.write_text("a sufficiently long secret", encoding="utf-8")
    with pytest.raises(RuntimeError):
        serve_peer(tmp_path / "catalog.json", secret, "0.0.0.0", 0, False)


def test_peer_state_prevents_replay_and_enforces_call_budget():
    from minexfabric.demo import demo_catalog
    from minexfabric.lease import create_lease
    from minexfabric.models import manifests_from_iterable
    from minexfabric.peer import PeerState

    secret = b"a sufficiently long shared secret"
    cap = next(c for c in manifests_from_iterable(demo_catalog()) if c.capability_id == "local-text-stats")
    state = PeerState([cap], secret)
    lease = create_lease(cap.capability_id, cap.provider_id, "consumer-a", secret, max_calls=1, owner_realm=cap.owner_realm)
    first = state.reserve_call("request-1", lease, cap, "consumer-a")
    assert first["valid"] is True
    replay = state.reserve_call("request-1", lease, cap, "consumer-a")
    assert replay["valid"] is False
    second = state.reserve_call("request-2", lease, cap, "consumer-a")
    assert second["valid"] is False
    assert "CALL_BUDGET_EXHAUSTED" in second["reasons"]
