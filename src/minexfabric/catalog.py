from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import CapabilityManifest, manifests_from_iterable
from .util import MinExError


def load_catalog(path: Path) -> list[CapabilityManifest]:
    if path.is_dir():
        entries = []
        for item in sorted(path.glob("*.json")):
            data = json.loads(item.read_text(encoding="utf-8"))
            if isinstance(data, list):
                entries.extend(data)
            else:
                entries.append(data)
        return manifests_from_iterable(entries)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "capabilities" in data:
        data = data["capabilities"]
    if not isinstance(data, list):
        raise MinExError("Catalog JSON must contain a list or {'capabilities': [...]} object")
    return manifests_from_iterable(data)


def catalog_to_dict(catalog: Iterable[CapabilityManifest]) -> dict:
    items = [cap.to_dict() for cap in catalog]
    return {"capability_count": len(items), "capabilities": items}
