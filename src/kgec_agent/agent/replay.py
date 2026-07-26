"""Executable eight-tool offline replay engine."""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from kgec_agent.calibration.service import CalibrationService
from kgec_agent.constraints.engine import SemanticValidator
from kgec_agent.decision.engine import DecisionEngine
from kgec_agent.evidence.sources import EvidenceSourceRegistry, LocalEvidenceSource
from kgec_agent.graph.service import CandidateGraphService
from kgec_agent.interfaces.registry import tool_names
from kgec_agent.llm.providers import FixtureLLMProvider
from kgec_agent.policy.engine import ConfidencePolicy
from kgec_agent.prediction.fixture import FixturePredictionService
from kgec_agent.provenance.exporter import ProvenanceExporter
from kgec_agent.runtime.hashing import sha256_json
from kgec_agent.schemas.models import (
    ReplayResult,
    RunRecord,
    ScenarioFixture,
    ToolInvocation,
)


class ReplayFailure(RuntimeError):
    pass


T = TypeVar("T")


def available_scenarios() -> tuple[str, ...]:
    return (
        "canonical_accept",
        "canonical_verify_review",
        "canonical_reject_abstain",
    )


def load_fixture(scenario_id: str) -> ScenarioFixture:
    if scenario_id not in available_scenarios():
        raise ValueError(f"unknown scenario: {scenario_id}")
    fixture = resources.files("kgec_agent.demo.fixtures").joinpath(f"{scenario_id}.json")
    return ScenarioFixture.model_validate_json(fixture.read_text(encoding="utf-8"))


class ReplayEngine:
    def __init__(self, fixture: ScenarioFixture) -> None:
        self.fixture = fixture
        self.invocations: list[ToolInvocation] = []

    def _invoke(self, name: str, inputs: Any, operation: Callable[[], T]) -> T:
        if name != tool_names()[len(self.invocations)]:
            raise ReplayFailure(f"unexpected tool order at {name}")
        input_hash = sha256_json(inputs)
        try:
            output = operation()
        except Exception as exc:
            self.invocations.append(
                ToolInvocation(
                    order=len(self.invocations) + 1,
                    tool_name=name,
                    status="failure",
                    input_hash=input_hash,
                    error=f"{type(exc).__name__}: {exc}",
                    reason_codes=["TOOL_FAILURE_RECORDED"],
                )
            )
            raise ReplayFailure(f"{name} failed") from exc
        reasons = list(getattr(output, "reason_codes", []))
        self.invocations.append(
            ToolInvocation(
                order=len(self.invocations) + 1,
                tool_name=name,
                status="success",
                input_hash=input_hash,
                output_hash=sha256_json(output),
                reason_codes=reasons,
            )
        )
        return output

    def replay(
        self,
        output_dir: Path,
        *,
        natural_language_request: str | None = None,
    ) -> ReplayResult:
        request = natural_language_request or self.fixture.natural_language_request
        provider = FixtureLLMProvider(self.fixture)
        orchestration = provider.map_request(request)
        if tuple(orchestration.tool_plan) != tool_names():
            raise ReplayFailure("LLM tool plan is not canonical")

        prediction = self._invoke(
            "predict_link",
            orchestration.query,
            lambda: FixturePredictionService().predict_link(orchestration.query, self.fixture),
        )
        calibration = self._invoke(
            "calibrate_prediction",
            prediction,
            lambda: CalibrationService().calibrate_prediction(prediction),
        )
        policy = self._invoke(
            "apply_confidence_policy",
            {"calibration": calibration, "thresholds": self.fixture.thresholds},
            lambda: ConfidencePolicy().apply_confidence_policy(
                calibration, self.fixture.thresholds
            ),
        )
        top_candidate = calibration.candidates[0]
        evidence_registry = EvidenceSourceRegistry()
        evidence_registry.register(
            "local",
            LocalEvidenceSource(
                self.fixture.evidence,
                required=policy.initial_route == "verify",
            ),
        )
        evidence = self._invoke(
            "retrieve_evidence",
            {
                "query": orchestration.query,
                "candidate": top_candidate,
                "source": "local",
                "required": policy.initial_route == "verify",
            },
            lambda: evidence_registry.get("local").retrieve(
                orchestration.query, top_candidate
            ),
        )
        semantics = self._invoke(
            "check_semantic_constraints",
            {
                "query": orchestration.query,
                "candidate": top_candidate,
                "context": self.fixture.constraints,
            },
            lambda: SemanticValidator().check_semantic_constraints(
                orchestration.query, top_candidate, self.fixture.constraints
            ),
        )
        decision = self._invoke(
            "make_final_decision",
            {"policy": policy, "evidence": evidence, "semantics": semantics},
            lambda: DecisionEngine().make_final_decision(policy, evidence, semantics),
        )
        graph = self._invoke(
            "propose_kg_update",
            {
                "query": orchestration.query,
                "candidate": top_candidate,
                "decision": decision,
            },
            lambda: CandidateGraphService().propose_kg_update(
                orchestration.query, top_candidate, decision
            ),
        )

        run_id = "run-" + sha256_json(
            {
                "scenario": self.fixture.scenario_id,
                "query": orchestration.query,
                "candidates": calibration.candidates,
                "version": "1.0.0",
            }
        )[:24]
        export_descriptor = {
            "run_id": run_id,
            "formats": ["json", "csv", "turtle", "markdown"],
            "filenames": [
                f"{self.fixture.scenario_id}.json",
                f"{self.fixture.scenario_id}.csv",
                f"{self.fixture.scenario_id}.ttl",
                f"{self.fixture.scenario_id}.md",
            ],
        }
        self._invoke("export_provenance", {"run_id": run_id}, lambda: export_descriptor)

        explanation = provider.explain(
            {
                "scenario_id": self.fixture.scenario_id,
                "initial_route": policy.initial_route,
                "evidence": evidence.outcome,
                "final_decision": decision.final_decision,
                "destination": decision.destination,
            }
        )
        reasons: list[str] = []
        for source in (
            prediction.reason_codes,
            calibration.reason_codes,
            policy.reason_codes,
            evidence.reason_codes,
            semantics.reason_codes,
            decision.reason_codes,
            graph.reason_codes,
        ):
            for reason in source:
                if reason not in reasons:
                    reasons.append(reason)
        record = RunRecord(
            run_id=run_id,
            scenario_id=self.fixture.scenario_id,
            stable_event_order=list(range(1, 9)),
            natural_language_request=request,
            structured_query=orchestration.query,
            candidates=calibration.candidates,
            raw_scores=[item.raw_score for item in calibration.candidates],
            calibrated_probabilities=[
                item.calibrated_probability for item in calibration.candidates
            ],
            confidence=calibration.confidence,
            margin=calibration.margin,
            thresholds=policy.thresholds,
            initial_route=policy.initial_route,
            evidence=evidence,
            semantic_checks=semantics.checks,
            final_decision=decision.final_decision,
            destination=decision.destination,
            reason_codes=reasons,
            tool_invocations=self.invocations,
            llm_explanation=explanation,
            content_hash="",
        )
        record.content_hash = sha256_json(
            record.model_dump(mode="json", exclude={"content_hash"})
        )
        expected = self.fixture.expected
        observed = (
            record.initial_route,
            record.evidence.outcome,
            record.final_decision,
            record.destination,
        )
        required = (
            expected.initial_route,
            expected.evidence_outcome,
            expected.final_decision,
            expected.destination,
        )
        if observed != required:
            raise ReplayFailure(f"fixture expectation mismatch: {observed!r} != {required!r}")

        paths = ProvenanceExporter().export_all(record, Path(output_dir))
        return ReplayResult(
            run=record,
            export_paths={name: str(path) for name, path in paths.items()},
        )


def replay_scenario(
    scenario_id: str,
    output_dir: Path,
    *,
    natural_language_request: str | None = None,
) -> ReplayResult:
    return ReplayEngine(load_fixture(scenario_id)).replay(
        Path(output_dir),
        natural_language_request=natural_language_request,
    )
