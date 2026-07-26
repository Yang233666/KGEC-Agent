#!/usr/bin/env python3
"""Fail-closed validator for the exact reviewer-facing candidate tree."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ZERO_HASH = "0" * 64
MAX_FILE_SIZE = 5 * 1024 * 1024
DENIED_SUFFIXES = {
    ".zip",
    ".7z",
    ".tar",
    ".gz",
    ".pickle",
    ".pkl",
    ".pt",
    ".pth",
    ".ckpt",
    ".bin",
    ".safetensors",
    ".onnx",
    ".npy",
    ".npz",
    ".pdf",
    ".tex",
}
IGNORED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "build",
    "dist",
    "runtime-output",
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def ignored(path: Path) -> bool:
    return (
        bool(set(path.parts) & IGNORED_PARTS)
        or any(part.endswith(".egg-info") for part in path.parts)
        or path.suffix in {".pyc", ".pyo"}
    )


def canonical_manifest_hash(document: dict[str, object]) -> str:
    normalized = json.loads(json.dumps(document))
    for entry in normalized["files"]:
        if entry["path"] in {"release-manifest.json", "SHA256SUMS"}:
            entry["sha256"] = ZERO_HASH
    payload = (json.dumps(normalized, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return sha256_bytes(payload)


def scan_text(path: str, text: str) -> list[str]:
    errors: list[str] = []
    private_tokens = [
        "/" + "Users/",
        "/" + "home/" + "yanyan",
        "remote" + "_folder",
        "BEGIN " + "PRIVATE KEY",
    ]
    for token in private_tokens:
        if token in text:
            errors.append(f"private or credential path token in {path}")
    secret_patterns = [
        re.compile("s" + r"k-[A-Za-z0-9_-]{20,}"),
        re.compile("g" + r"hp_[A-Za-z0-9]{20,}"),
        re.compile(
            r"(?i)(api[_-]?key|password|access[_-]?token)\s*[:=]\s*[\"'][A-Za-z0-9_./+-]{16,}[\"']"
        ),
    ]
    if any(pattern.search(text) for pattern in secret_patterns):
        errors.append(f"credential-like literal in {path}")
    placeholders = [
        "TODO" + "_PUBLIC",
        "LICENSE" + "_PENDING",
        "VIDEO" + "_URL_PENDING",
    ]
    for placeholder in placeholders:
        if placeholder in text and not (
            placeholder == "VIDEO" + "_URL_PENDING" and path == "docs/media.md"
        ):
            errors.append(f"unresolved placeholder {placeholder} in {path}")
    return errors


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / "release-manifest.json"
    sums_path = root / "SHA256SUMS"
    if not manifest_path.is_file() or not sums_path.is_file():
        return ["release-manifest.json and SHA256SUMS are required"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [f"manifest parse failure: {exc}"]
    entries = manifest.get("files", [])
    paths = [entry.get("path") for entry in entries]
    if len(paths) != len(set(paths)):
        errors.append("duplicate manifest entry")
    for path in paths:
        if isinstance(path, str) and ".git" in Path(path).parts:
            errors.append(f"Git metadata declared in release manifest: {path}")

    actual = sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not ignored(path.relative_to(root))
    )
    declared = sorted(str(path) for path in paths)
    if actual != declared:
        missing = sorted(set(declared) - set(actual))
        extra = sorted(set(actual) - set(declared))
        errors.append(f"manifest file-set mismatch; missing={missing}; extra={extra}")

    canonical = canonical_manifest_hash(manifest)
    by_path = {str(entry["path"]): entry for entry in entries}
    for relative in actual:
        path = root / relative
        entry = by_path.get(relative)
        if entry is None:
            continue
        expected_hash = (
            canonical if relative == "release-manifest.json" else sha256_file(path)
        )
        if entry.get("sha256") != expected_hash:
            errors.append(f"changed hash: {relative}")
        if entry.get("size") != path.stat().st_size:
            errors.append(f"changed size: {relative}")
        if path.stat().st_size > MAX_FILE_SIZE:
            errors.append(f"oversized public file: {relative}")
        if path.name == ".DS_Store":
            errors.append(f"macOS metadata denied: {relative}")
        if path.suffix.lower() in DENIED_SUFFIXES:
            errors.append(f"denied file type: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        errors.extend(scan_text(relative, text))

    lines = [
        line
        for line in sums_path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    sums: dict[str, str] = {}
    for line in lines:
        try:
            digest, relative = line.split("  ", 1)
        except ValueError:
            errors.append("malformed SHA256SUMS line")
            continue
        if relative in sums:
            errors.append(f"duplicate SHA256SUMS entry: {relative}")
        sums[relative] = digest
    expected_sum_paths = set(actual) - {"SHA256SUMS"}
    if set(sums) != expected_sum_paths:
        errors.append("SHA256SUMS file-set mismatch")
    for relative, digest in sums.items():
        expected = (
            canonical if relative == "release-manifest.json" else sha256_file(root / relative)
        )
        if digest != expected:
            errors.append(f"SHA256SUMS mismatch: {relative}")
    return errors


if __name__ == "__main__":
    candidate_root = Path(__file__).resolve().parents[1]
    findings = validate(candidate_root)
    if findings:
        for finding in findings:
            print(f"ERROR={finding}", file=sys.stderr)
        raise SystemExit(1)
    print("PUBLIC_RELEASE_VALIDATION=PASS")
