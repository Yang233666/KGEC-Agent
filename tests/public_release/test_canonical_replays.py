from kgec_agent.agent.replay import replay_scenario
from kgec_agent.schemas.models import TOOL_NAMES


EXPECTED = {
    "canonical_accept": ("auto_accept", "accepted", "accepted_candidate_graph"),
    "canonical_verify_review": ("verify", "human_review", "human_review_queue"),
    "canonical_reject_abstain": ("auto_accept", "rejected", "rejection_state"),
}


def test_all_canonical_replays(tmp_path):
    for scenario, expected in EXPECTED.items():
        result = replay_scenario(scenario, tmp_path / scenario)
        assert (
            result.run.initial_route,
            result.run.final_decision,
            result.run.destination,
        ) == expected
        assert tuple(item.tool_name for item in result.run.tool_invocations) == TOOL_NAMES
        assert [item.order for item in result.run.tool_invocations] == list(range(1, 9))
