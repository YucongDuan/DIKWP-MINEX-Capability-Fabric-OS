from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass
class Measurement:
    wall_ms: float
    cpu_ms: float
    energy_j: float | None
    source: str

    def to_dict(self) -> dict:
        return {
            "wall_ms": round(self.wall_ms, 6),
            "cpu_ms": round(self.cpu_ms, 6),
            "energy_j": None if self.energy_j is None else round(self.energy_j, 9),
            "source": self.source,
        }


def _rapl_paths() -> list[Path]:
    root = Path("/sys/class/powercap")
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("energy_uj") if path.is_file())


def _read_rapl() -> tuple[float | None, list[Path]]:
    paths = _rapl_paths()
    if not paths:
        return None, []
    total = 0.0
    usable: list[Path] = []
    for path in paths:
        try:
            total += float(path.read_text().strip()) / 1_000_000.0
            usable.append(path)
        except (OSError, ValueError):
            continue
    return (total if usable else None), usable


def measure_call(fn: Callable[[], T]) -> tuple[T, Measurement]:
    energy_before, paths_before = _read_rapl()
    wall_before = time.perf_counter()
    cpu_before = time.process_time()
    result = fn()
    cpu_after = time.process_time()
    wall_after = time.perf_counter()
    energy_after, paths_after = _read_rapl()
    energy = None
    source = "unmeasured"
    if energy_before is not None and energy_after is not None and paths_before == paths_after:
        delta = energy_after - energy_before
        if delta >= 0:
            energy = delta
            source = "linux-rapl"
    return result, Measurement(
        wall_ms=(wall_after - wall_before) * 1000.0,
        cpu_ms=(cpu_after - cpu_before) * 1000.0,
        energy_j=energy,
        source=source,
    )
