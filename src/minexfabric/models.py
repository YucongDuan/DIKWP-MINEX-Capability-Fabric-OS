from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable

from .util import MinExError, clamp, finite_nonnegative, sha256_json


class Surface(str, Enum):
    MODEL_NATIVE = "model_native"
    LOCAL_CODE = "local_code"
    LOCAL_API = "local_api"
    LOCAL_GUI = "local_gui"
    SAME_OWNER_PEER = "same_owner_peer"
    MARKET_SERVICE = "market_service"
    HUMAN_DELEGATE = "human_delegate"
    RECIPE = "recipe"


class SideEffect(str, Enum):
    NONE = "none"
    REVERSIBLE_LOCAL = "reversible_local"
    REVERSIBLE_EXTERNAL = "reversible_external"
    IRREVERSIBLE_EXTERNAL = "irreversible_external"


SIDE_EFFECT_ORDER = {
    SideEffect.NONE.value: 0,
    SideEffect.REVERSIBLE_LOCAL.value: 1,
    SideEffect.REVERSIBLE_EXTERNAL.value: 2,
    SideEffect.IRREVERSIBLE_EXTERNAL.value: 3,
}


@dataclass(frozen=True)
class CostVector:
    energy_j: float = 0.0
    verification_energy_j: float = 0.0
    coordination_energy_j: float = 0.0
    retry_energy_j: float = 0.0
    latency_ms: float = 0.0
    money: float = 0.0
    human_minutes: float = 0.0
    data_exposure: float = 0.0
    carbon_g: float = 0.0
    semantic_loss: float = 0.0
    failure_probability: float = 0.0
    measurement_source: str = "declared"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "CostVector":
        data = data or {}
        kwargs = {}
        for name in (
            "energy_j", "verification_energy_j", "coordination_energy_j", "retry_energy_j",
            "latency_ms", "money", "human_minutes", "carbon_g",
        ):
            kwargs[name] = finite_nonnegative(data.get(name, 0.0), name)
        for name in ("data_exposure", "semantic_loss", "failure_probability"):
            kwargs[name] = clamp(float(data.get(name, 0.0)))
        kwargs["measurement_source"] = str(data.get("measurement_source", "declared"))
        return cls(**kwargs)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def expected_energy_j(self) -> float:
        base = self.energy_j + self.verification_energy_j + self.coordination_energy_j
        p = min(self.failure_probability, 0.999999)
        expected_retries = p / max(1e-9, 1.0 - p)
        return base + expected_retries * self.retry_energy_j


@dataclass(frozen=True)
class CapabilityManifest:
    capability_id: str
    name: str
    description: str
    provider_id: str
    owner_realm: str
    surface: str
    requires: tuple[str, ...]
    provides: tuple[str, ...]
    cost: CostVector
    quality: float
    authority_scopes: tuple[str, ...] = ()
    side_effect: str = SideEffect.NONE.value
    deterministic: bool = False
    cacheable: bool = False
    availability: bool = True
    executor: dict[str, Any] = field(default_factory=dict)
    terms: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CapabilityManifest":
        required = ["capability_id", "name", "provider_id", "owner_realm", "surface", "requires", "provides"]
        missing = [key for key in required if key not in data]
        if missing:
            raise MinExError(f"Capability manifest missing fields: {', '.join(missing)}")
        try:
            Surface(str(data["surface"]))
        except ValueError as exc:
            raise MinExError(f"Unsupported surface: {data['surface']}") from exc
        side_effect = str(data.get("side_effect", SideEffect.NONE.value))
        if side_effect not in SIDE_EFFECT_ORDER:
            raise MinExError(f"Unsupported side effect: {side_effect}")
        requires = tuple(sorted({str(x) for x in data.get("requires", [])}))
        provides = tuple(sorted({str(x) for x in data.get("provides", [])}))
        if not provides:
            raise MinExError("A capability must provide at least one semantic type")
        return cls(
            capability_id=str(data["capability_id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            provider_id=str(data["provider_id"]),
            owner_realm=str(data["owner_realm"]),
            surface=str(data["surface"]),
            requires=requires,
            provides=provides,
            cost=CostVector.from_dict(data.get("cost")),
            quality=clamp(float(data.get("quality", 0.5))),
            authority_scopes=tuple(sorted({str(x) for x in data.get("authority_scopes", [])})),
            side_effect=side_effect,
            deterministic=bool(data.get("deterministic", False)),
            cacheable=bool(data.get("cacheable", False)),
            availability=bool(data.get("availability", True)),
            executor=dict(data.get("executor", {})),
            terms=dict(data.get("terms", {})),
            provenance=dict(data.get("provenance", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["requires"] = list(self.requires)
        result["provides"] = list(self.provides)
        result["authority_scopes"] = list(self.authority_scopes)
        result["cost"] = self.cost.to_dict()
        return result

    @property
    def digest(self) -> str:
        return sha256_json(self.to_dict())


@dataclass(frozen=True)
class IntentSpec:
    intent_id: str
    title: str
    purpose: str
    available_types: tuple[str, ...]
    required_types: tuple[str, ...]
    inputs: dict[str, Any]
    granted_scopes: tuple[str, ...]
    constraints: dict[str, Any]
    weights: dict[str, float]
    owner_realm: str = "local-owner"
    currency: str = "USD"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IntentSpec":
        required = ["intent_id", "title", "purpose", "available_types", "required_types"]
        missing = [key for key in required if key not in data]
        if missing:
            raise MinExError(f"Intent missing fields: {', '.join(missing)}")
        weights = {str(k): finite_nonnegative(v, f"weight.{k}") for k, v in dict(data.get("weights", {})).items()}
        if not weights:
            weights = {
                "expected_energy_j": 0.28,
                "latency_ms": 0.12,
                "money": 0.12,
                "human_minutes": 0.12,
                "data_exposure": 0.10,
                "carbon_g": 0.06,
                "semantic_loss": 0.10,
                "failure_probability": 0.10,
            }
        total = sum(weights.values())
        if total <= 0:
            raise MinExError("At least one preference weight must be positive")
        weights = {k: v / total for k, v in weights.items()}
        return cls(
            intent_id=str(data["intent_id"]),
            title=str(data["title"]),
            purpose=str(data["purpose"]),
            available_types=tuple(sorted({str(x) for x in data.get("available_types", [])})),
            required_types=tuple(sorted({str(x) for x in data.get("required_types", [])})),
            inputs=dict(data.get("inputs", {})),
            granted_scopes=tuple(sorted({str(x) for x in data.get("granted_scopes", [])})),
            constraints=dict(data.get("constraints", {})),
            weights=weights,
            owner_realm=str(data.get("owner_realm", "local-owner")),
            currency=str(data.get("currency", "USD")),
        )

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["available_types"] = list(self.available_types)
        result["required_types"] = list(self.required_types)
        result["granted_scopes"] = list(self.granted_scopes)
        return result

    @property
    def digest(self) -> str:
        return sha256_json(self.to_dict())


@dataclass
class RoutePlan:
    route_id: str
    capability_ids: list[str]
    final_types: list[str]
    cost: dict[str, Any]
    quality: float
    score: float
    admissible: bool
    gate_reasons: list[str]
    pareto: bool = False
    execution_status: str = "planned"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def manifests_from_iterable(items: Iterable[dict[str, Any]]) -> list[CapabilityManifest]:
    manifests = [CapabilityManifest.from_dict(item) for item in items]
    ids = [item.capability_id for item in manifests]
    if len(ids) != len(set(ids)):
        raise MinExError("Duplicate capability_id in catalog")
    return manifests
