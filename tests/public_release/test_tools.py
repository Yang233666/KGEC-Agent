from kgec_agent.agent.replay import replay_scenario
from kgec_agent.interfaces.registry import TOOL_REGISTRY, tool_names
from kgec_agent.schemas.models import TOOL_NAMES


def test_exactly_eight_registered_tools_are_invoked(tmp_path):
    assert len(TOOL_REGISTRY) == 8
    assert tool_names() == TOOL_NAMES
    result = replay_scenario("canonical_accept", tmp_path)
    invocations = result.run.tool_invocations
    assert tuple(item.tool_name for item in invocations) == TOOL_NAMES
    assert all(item.status == "success" for item in invocations)
    assert all(len(item.input_hash) == 64 for item in invocations)
    assert all(item.output_hash and len(item.output_hash) == 64 for item in invocations)
