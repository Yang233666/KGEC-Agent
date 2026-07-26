import importlib.util
import json
from pathlib import Path


def test_complete_public_manifest():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "validate_public_release.py"
    spec = importlib.util.spec_from_file_location("public_validator", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert module.validate(root) == []
    manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
    assert not any(".git" in Path(item["path"]).parts for item in manifest["files"])
    assert module.ignored(Path(".git/config"))


def test_git_metadata_cannot_be_declared(tmp_path):
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts" / "validate_public_release.py"
    spec = importlib.util.spec_from_file_location("public_validator_git", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
    manifest["files"].append(
        {
            "path": ".git/config",
            "size": 0,
            "sha256": "0" * 64,
            "classification": "release_metadata",
            "licence_provenance": "generated_release_integrity_metadata",
        }
    )
    (tmp_path / "release-manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (tmp_path / "SHA256SUMS").write_text("", encoding="utf-8")
    findings = module.validate(tmp_path)
    assert "Git metadata declared in release manifest: .git/config" in findings
