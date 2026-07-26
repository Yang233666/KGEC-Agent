import socket
import urllib.request

from kgec_agent.agent.replay import available_scenarios, replay_scenario
from kgec_agent.evidence.sources import SPARQLEvidenceSource
from kgec_agent.llm.providers import LiveStructuredLLMProvider


def test_replays_do_not_open_network_or_live_adapters(monkeypatch, tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("offline replay attempted a forbidden live integration")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    monkeypatch.setattr(LiveStructuredLLMProvider, "__init__", forbidden)
    monkeypatch.setattr(SPARQLEvidenceSource, "__init__", forbidden)
    for scenario in available_scenarios():
        result = replay_scenario(scenario, tmp_path / scenario)
        assert result.run.execution_mode == "offline_fixture_replay"
