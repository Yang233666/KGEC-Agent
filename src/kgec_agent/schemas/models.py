"""Validated data contracts shared by the replay, tools, UI, and exporters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TOOL_NAMES = (
    "predict_link",
    "calibrate_prediction",
    "apply_confidence_policy",
    "retrieve_evidence",
    "check_semantic_constraints",
    "make_final_decision",
    "propose_kg_update",
    "export_provenance",
)
CONSTRAINT_CATEGORIES = (
    "domain",
    "range",
    "entity_type",
    "duplicate",
    "contradiction",
    "functional_property",
    "inverse_relation",
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StructuredQuery(StrictModel):
    subject: str = Field(min_length=1)
    relation: str = Field(min_length=1)
    direction: Literal["head", "tail"] = "tail"
    top_k: int = Field(default=3, ge=1, le=10)
    natural_language: str = Field(min_length=1)


class Candidate(StrictModel):
    entity: str = Field(min_length=1)
    label: str = Field(min_length=1)
    entity_type: str = Field(min_length=1)
    raw_score: float
    calibrated_probability: float = Field(ge=0.0, le=1.0)


class PolicyThresholds(StrictModel):
    accept_threshold: float = Field(ge=0.0, le=1.0)
    verify_threshold: float = Field(ge=0.0, le=1.0)
    margin_threshold: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_order(self) -> "PolicyThresholds":
        if self.verify_threshold > self.accept_threshold:
            raise ValueError("verify_threshold must not exceed accept_threshold")
        return self


class PredictionResult(StrictModel):
    query: StructuredQuery
    candidates: list[Candidate] = Field(min_length=2)
    source: Literal["offline_fixture"] = "offline_fixture"
    reason_codes: list[str]


class CalibrationResult(StrictModel):
    candidates: list[Candidate] = Field(min_length=2)
    confidence: float = Field(ge=0.0, le=1.0)
    margin: float = Field(ge=0.0, le=1.0)
    method: Literal["frozen_calibration_fixture"] = "frozen_calibration_fixture"
    reason_codes: list[str]


class PolicyResult(StrictModel):
    initial_route: Literal["auto_accept", "verify", "abstain"]
    confidence: float
    margin: float
    thresholds: PolicyThresholds
    reason_codes: list[str]


class EvidenceResult(StrictModel):
    source: str
    outcome: Literal[
        "supporting",
        "contradicting",
        "not_found",
        "unavailable",
        "error",
        "not_requested",
    ]
    detail: str
    reason_codes: list[str]


class ConstraintCheck(StrictModel):
    category: Literal[
        "domain",
        "range",
        "entity_type",
        "duplicate",
        "contradiction",
        "functional_property",
        "inverse_relation",
    ]
    passed: bool
    blocking: bool
    reason_code: str
    detail: str


class SemanticResult(StrictModel):
    checks: list[ConstraintCheck]
    blocking_violations: list[str]
    reason_codes: list[str]


class DecisionResult(StrictModel):
    final_decision: Literal["accepted", "human_review", "rejected", "abstained"]
    destination: Literal[
        "accepted_candidate_graph",
        "human_review_queue",
        "rejection_state",
        "abstention_state",
    ]
    reason_codes: list[str]


class GraphUpdateResult(StrictModel):
    operation: Literal["stage_candidate", "route_for_review", "record_rejection", "record_abstention"]
    destination: str
    candidate_triple: tuple[str, str, str]
    production_graph_modified: Literal[False] = False
    reason_codes: list[str]


class ToolInvocation(StrictModel):
    order: int = Field(ge=1)
    tool_name: str
    status: Literal["success", "failure"]
    input_hash: str
    output_hash: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    error: str | None = None


class LLMStructuredResponse(StrictModel):
    query: StructuredQuery
    tool_plan: list[str]

    @model_validator(mode="after")
    def validate_tool_plan(self) -> "LLMStructuredResponse":
        if tuple(self.tool_plan) != TOOL_NAMES:
            raise ValueError("tool_plan must contain the canonical eight tools in order")
        return self


class ExplanationOutput(StrictModel):
    explanation: str = Field(min_length=1, max_length=1200)


class ConstraintContext(StrictModel):
    subject_type: str
    expected_domain: str
    expected_range: str
    allowed_candidate_types: list[str]
    existing_triples: list[tuple[str, str, str]] = Field(default_factory=list)
    contradicting_triples: list[tuple[str, str, str]] = Field(default_factory=list)
    functional_property: bool = False
    existing_functional_objects: list[str] = Field(default_factory=list)
    inverse_relation: str | None = None
    inverse_triples: list[tuple[str, str, str]] = Field(default_factory=list)
    blocking_categories: dict[str, bool]

    @model_validator(mode="after")
    def validate_categories(self) -> "ConstraintContext":
        if set(self.blocking_categories) != set(CONSTRAINT_CATEGORIES):
            raise ValueError("blocking_categories must define all seven semantic categories")
        return self


class EvidenceFixture(StrictModel):
    outcome: Literal["supporting", "contradicting", "not_found"]
    detail: str


class ExpectedOutcome(StrictModel):
    initial_route: Literal["auto_accept", "verify", "abstain"]
    evidence_outcome: str
    final_decision: Literal["accepted", "human_review", "rejected", "abstained"]
    destination: str


class ScenarioFixture(StrictModel):
    schema_version: Literal["1.0.0"]
    scenario_id: str
    title: str
    disclosure: str
    natural_language_request: str
    llm: LLMStructuredResponse
    candidates: list[Candidate] = Field(min_length=3)
    thresholds: PolicyThresholds
    evidence: EvidenceFixture
    constraints: ConstraintContext
    expected: ExpectedOutcome

    @model_validator(mode="after")
    def validate_fixture(self) -> "ScenarioFixture":
        if self.llm.query.natural_language != self.natural_language_request:
            raise ValueError("fixture query must retain the natural-language request")
        if self.llm.query.top_k != len(self.candidates):
            raise ValueError("top_k must match packaged candidates")
        return self


class RunRecord(StrictModel):
    schema_version: Literal["1.0.0"] = "1.0.0"
    implementation_version: Literal["1.0.0"] = "1.0.0"
    run_id: str
    scenario_id: str
    execution_mode: Literal["offline_fixture_replay"] = "offline_fixture_replay"
    stable_event_order: list[int]
    natural_language_request: str
    structured_query: StructuredQuery
    candidates: list[Candidate]
    raw_scores: list[float]
    calibrated_probabilities: list[float]
    confidence: float
    margin: float
    thresholds: PolicyThresholds
    initial_route: str
    evidence: EvidenceResult
    semantic_checks: list[ConstraintCheck]
    final_decision: str
    destination: str
    reason_codes: list[str]
    tool_invocations: list[ToolInvocation]
    llm_explanation: str
    content_hash: str


class ReplayResult(StrictModel):
    run: RunRecord
    export_paths: dict[str, str]
