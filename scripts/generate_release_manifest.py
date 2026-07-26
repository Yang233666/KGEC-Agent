#!/usr/bin/env python3
"""Generate the complete deterministic release manifest and checksum file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ZERO_HASH = "0" * 64
MANIFEST = "release-manifest.json"
SUMS = "SHA256SUMS"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ignored(path: Path) -> bool:
    parts = set(path.parts)
    return (
        ".git" in parts
        or "__pycache__" in parts
        or ".pytest_cache" in parts
        or ".venv" in parts
        or "build" in parts
        or "dist" in parts
        or "runtime-output" in parts
        or any(part.endswith(".egg-info") for part in path.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def classification(path: str) -> str:
    if path.startswith("src/") or path.startswith("apps/"):
        return "source"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("configs/"):
        return "configuration"
    if path.startswith("examples/exports/"):
        return "generated_example"
    if path.startswith("examples/"):
        return "fixture"
    if path.startswith("figures/") or path.startswith("media/"):
        return "figure"
    if path.startswith("docs/") or path == "README.md":
        return "documentation"
    if path.startswith("scripts/"):
        return "release_tool"
    if path.startswith(".github/"):
        return "ci_configuration"
    return "release_metadata"


def provenance(path: str) -> str:
    if path.startswith("figures/") or path.startswith("media/"):
        return "author_generated_project_asset"
    if path.startswith("examples/exports/"):
        return "generated_by_kgec_agent_1.0.0"
    if path in {MANIFEST, SUMS}:
        return "generated_release_integrity_metadata"
    return "original_kgec_agent_mit"


def render(entries: list[dict[str, object]]) -> bytes:
    document = {
        "schema_version": "1.0.0",
        "release_version": "1.0.0",
        "ordering": "UTF-8 relative path ascending",
        "manifest_self_hash_rule": (
            "For the release-manifest.json entry, SHA-256 is computed over this JSON "
            "with the sha256 values for release-manifest.json and SHA256SUMS replaced "
            "by 64 zeroes. Fixed-width replacement avoids self-reference."
        ),
        "checksum_rule": (
            "SHA256SUMS covers every public release file except itself. Its manifest line "
            "uses the canonical manifest digest defined above."
        ),
        "files": entries,
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def generate(root: Path) -> tuple[str, str]:
    root = root.resolve()
    regular_paths = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.name not in {MANIFEST, SUMS}
        and not ignored(path.relative_to(root))
    )
    entries = [
        {
            "path": relative,
            "size": (root / relative).stat().st_size,
            "sha256": sha256(root / relative),
            "classification": classification(relative),
            "licence_provenance": provenance(relative),
        }
        for relative in regular_paths
    ]
    entries.extend(
        [
            {
                "path": MANIFEST,
                "size": 0,
                "sha256": ZERO_HASH,
                "classification": "release_metadata",
                "licence_provenance": provenance(MANIFEST),
            },
            {
                "path": SUMS,
                "size": 0,
                "sha256": ZERO_HASH,
                "classification": "release_metadata",
                "licence_provenance": provenance(SUMS),
            },
        ]
    )
    entries.sort(key=lambda item: str(item["path"]))

    checksum_header = (
        "# release-manifest.json uses the canonical digest defined inside that file; "
        "SHA256SUMS excludes itself.\n"
    )
    checksum_paths = sorted([*regular_paths, MANIFEST])
    checksum_size = len(checksum_header.encode("utf-8")) + sum(
        len(f"{ZERO_HASH}  {path}\n".encode("utf-8")) for path in checksum_paths
    )
    by_path = {str(item["path"]): item for item in entries}
    by_path[SUMS]["size"] = checksum_size

    previous_size = -1
    while previous_size != int(by_path[MANIFEST]["size"]):
        previous_size = int(by_path[MANIFEST]["size"])
        by_path[MANIFEST]["size"] = len(render(entries))

    canonical_manifest = render(entries)
    canonical_hash = hashlib.sha256(canonical_manifest).hexdigest()
    checksum_lines = [checksum_header]
    for path in checksum_paths:
        value = canonical_hash if path == MANIFEST else str(by_path[path]["sha256"])
        checksum_lines.append(f"{value}  {path}\n")
    checksum_bytes = "".join(checksum_lines).encode("utf-8")
    if len(checksum_bytes) != checksum_size:
        raise RuntimeError("checksum size calculation is unstable")
    checksum_hash = hashlib.sha256(checksum_bytes).hexdigest()

    by_path[MANIFEST]["sha256"] = canonical_hash
    by_path[SUMS]["sha256"] = checksum_hash
    final_manifest = render(entries)
    if len(final_manifest) != int(by_path[MANIFEST]["size"]):
        raise RuntimeError("manifest size calculation is unstable")
    (root / MANIFEST).write_bytes(final_manifest)
    (root / SUMS).write_bytes(checksum_bytes)
    return canonical_hash, checksum_hash


if __name__ == "__main__":
    candidate_root = Path(__file__).resolve().parents[1]
    manifest_hash, sums_hash = generate(candidate_root)
    print(f"CANONICAL_MANIFEST_SHA256={manifest_hash}")
    print(f"SHA256SUMS_SHA256={sums_hash}")
