import json

import pytest

from kgec_agent.agent.replay import load_fixture, replay_scenario
from kgec_agent.llm.providers import (
    FixtureLLMProvider,
    LLMProviderResponseError,
    LiveLLMConfig,
    LiveStructuredLLMProvider,
)


def response_bytes(document):
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(document)}}]}
    ).encode("utf-8")


def test_fixture_maps_natural_language_deterministically():
    fixture = load_fixture("canonical_accept")
    provider = FixtureLLMProvider(fixture)
    first = provider.map_request(fixture.natural_language_request)
    second = provider.map_request(fixture.natural_language_request)
    assert first == second
    assert first.query.subject == "h_person"
    assert first.query.relation == "r_supports"


def test_live_structured_provider_accepts_valid_mocked_output():
    fixture = load_fixture("canonical_accept")
    config = LiveLLMConfig(
        endpoint_url="https://example.invalid/structured",
        model="mock-model",
        api_key="x",
        timeout_seconds=1,
    )
    provider = LiveStructuredLLMProvider(
        config,
        transport=lambda request, timeout: response_bytes(
            fixture.llm.model_dump(mode="json")
        ),
    )
    assert provider.map_request("request") == fixture.llm


def test_invalid_live_provider_output_is_rejected():
    config = LiveLLMConfig(
        endpoint_url="https://example.invalid/structured",
        model="mock-model",
        api_key="x",
        timeout_seconds=1,
    )
    provider = LiveStructuredLLMProvider(
        config,
        transport=lambda request, timeout: response_bytes({"query": {"bad": True}}),
    )
    with pytest.raises(LLMProviderResponseError):
        provider.map_request("request")


def test_explanation_cannot_overwrite_tool_outputs(tmp_path):
    result = replay_scenario("canonical_reject_abstain", tmp_path)
    before = result.run.model_dump(mode="json")
    fixture = load_fixture("canonical_reject_abstain")
    explanation = FixtureLLMProvider(fixture).explain(
        {
            "scenario_id": result.run.scenario_id,
            "initial_route": result.run.initial_route,
            "evidence": result.run.evidence.outcome,
            "final_decision": result.run.final_decision,
            "destination": result.run.destination,
        }
    )
    assert "rejected" in explanation
    assert result.run.model_dump(mode="json") == before
