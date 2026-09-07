from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


class MinExError(RuntimeError):
    """Base error for the reference implementation."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MinExError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MinExError(f"Invalid JSON in {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


def write_text(path: Path, value: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return min(high, max(low, float(value)))


def finite_nonnegative(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise MinExError(f"{name} must be numeric") from exc
    if not math.isfinite(result) or result < 0:
        raise MinExError(f"{name} must be finite and non-negative")
    return result


def stable_id(prefix: str, value: Any, length: int = 16) -> str:
    return f"{prefix}-{sha256_json(value)[:length]}"
