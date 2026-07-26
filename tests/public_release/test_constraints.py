import pytest

from kgec_agent.constraints.engine import SemanticValidator
from kgec_agent.decision.engine import DecisionEngine
from kgec_agent.agent.replay import load_fixture
from kgec_agent.schemas.models import EvidenceResult, PolicyResult


@pytest.mark.parametrize(
    ("category", "context_update", "candidate_update"),
    [
        ("domain", {"subject_type": "Wrong"}, {}),
        ("range", {}, {"entity_type": "Wrong"}),
        ("entity_type", {"allowed_candidate_types": ["Other"]}, {}),
        ("duplicate", {"existing_triples": [("h_person", "r_supports", "t_supported")]}, {}),
        ("contradiction", {"contradicting_triples": [("h_person", "r_supports", "t_supported")]}, {}),
        ("functional_property", {"functional_property": True, "existing_functional_objects": ["different"]}, {}),
        ("inverse_relation", {"inverse_triples": []}, {}),
    ],
)
def test_each_semantic_category_is_observable(category, context_update, candidate_update):
    fixture = load_fixture("canonical_accept")
    context = fixture.constraints.model_copy(update=context_update)
    candidate = fixture.candidates[0].model_copy(update=candidate_update)
    result = SemanticValidator().check_semantic_constraints(
        fixture.llm.query, candidate, context
    )
    selected = next(item for item in result.checks if item.category == category)
    assert selected.passed is False
    assert selected.reason_code.endswith("_VIOLATION")
    assert category in result.blocking_violations


def test_blocking_violation_overrides_high_confidence_acceptance():
    fixture = load_fixture("canonical_reject_abstain")
    semantics = SemanticValidator().check_semantic_constraints(
        fixture.llm.query, fixture.candidates[0], fixture.constraints
    )
    policy = PolicyResult(
        initial_route="auto_accept",
        confidence=0.91,
        margin=0.86,
        thresholds=fixture.thresholds,
        reason_codes=[],
    )
    evidence = EvidenceResult(
        source="local_fixture",
        outcome="not_requested",
        detail="not required",
        reason_codes=[],
    )
    decision = DecisionEngine().make_final_decision(policy, evidence, semantics)
    assert decision.final_decision == "rejected"
    assert decision.destination == "rejection_state"


def test_nonblocking_failure_is_explicit_but_does_not_block():
    fixture = load_fixture("canonical_accept")
    blocking = dict(fixture.constraints.blocking_categories)
    blocking["inverse_relation"] = False
    context = fixture.constraints.model_copy(
        update={"inverse_triples": [], "blocking_categories": blocking}
    )
    result = SemanticValidator().check_semantic_constraints(
        fixture.llm.query, fixture.candidates[0], context
    )
    inverse = next(item for item in result.checks if item.category == "inverse_relation")
    assert inverse.passed is False
    assert inverse.blocking is False
    assert result.blocking_violations == []
