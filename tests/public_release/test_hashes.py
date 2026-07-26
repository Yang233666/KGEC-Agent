import hashlib
from pathlib import Path

from kgec_agent.agent.replay import replay_scenario


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_replay_and_export_hashes_are_deterministic(tmp_path):
    first = replay_scenario("canonical_accept", tmp_path / "first")
    second = replay_scenario("canonical_accept", tmp_path / "second")
    assert first.run.content_hash == second.run.content_hash
    assert first.run.run_id == second.run.run_id
    for name in ("json", "csv", "turtle", "markdown"):
        assert digest(first.export_paths[name]) == digest(second.export_paths[name])
