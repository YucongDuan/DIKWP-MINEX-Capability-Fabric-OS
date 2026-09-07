from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_ROOTS = {
    ".git", ".pytest_cache", "__pycache__", "build", "dist", "build_artifacts",
    "delivery", "release", "validation",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def included(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDED_ROOTS or part.endswith(".egg-info") for part in rel.parts):
        return False
    if path.name == "SBOM.spdx.json" or path.suffix in {".pyc", ".pyo"}:
        return False
    return path.is_file()


def main() -> int:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not included(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        files.append({
            "SPDXID": "SPDXRef-File-" + hashlib.sha256(rel.encode("utf-8")).hexdigest()[:20],
            "fileName": rel,
            "checksums": [{"algorithm": "SHA256", "checksumValue": sha(path)}],
            "licenseConcluded": "NOASSERTION",
            "copyrightText": "NOASSERTION",
        })
    doc = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "DIKWP-MINEX-Capability-Fabric-OS-1.0.0",
        "documentNamespace": "https://github.com/YucongDuan/DIKWP-MINEX-Capability-Fabric-OS/releases/tag/v1.0.0/spdx",
        "creationInfo": {
            "created": datetime.now(timezone.utc).isoformat(),
            "creators": ["Tool: DIKWP-MINEX-generate-sbom"],
        },
        "packages": [{
            "name": "dikwp-minex",
            "SPDXID": "SPDXRef-Package",
            "versionInfo": "1.0.0",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": True,
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
            "copyrightText": "Copyright 2026 Yucong Duan",
        }],
        "files": files,
        "relationships": [
            {"spdxElementId": "SPDXRef-DOCUMENT", "relationshipType": "DESCRIBES", "relatedSpdxElement": "SPDXRef-Package"},
            *[
                {"spdxElementId": "SPDXRef-Package", "relationshipType": "CONTAINS", "relatedSpdxElement": item["SPDXID"]}
                for item in files
            ],
        ],
    }
    (ROOT / "SBOM.spdx.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "output": str(ROOT / 'SBOM.spdx.json')}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
