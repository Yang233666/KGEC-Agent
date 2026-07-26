"""Stable registry for the eight public tool roles."""

from __future__ import annotations

from dataclasses import dataclass

from kgec_agent.schemas.models import TOOL_NAMES


@dataclass(frozen=True)
class ToolRole:
    name: str
    purpose: str


TOOL_REGISTRY = (
    ToolRole("predict_link", "Load the fixture-backed Top-k link predictions."),
    ToolRole("calibrate_prediction", "Expose frozen calibrated probabilities and margin."),
    ToolRole("apply_confidence_policy", "Map confidence and margin to the initial route."),
    ToolRole("retrieve_evidence", "Retrieve normalized local or optional SPARQL evidence."),
    ToolRole("check_semantic_constraints", "Evaluate seven explicit semantic categories."),
    ToolRole("make_final_decision", "Combine policy, evidence, and blocking constraints."),
    ToolRole("propose_kg_update", "Route a candidate without modifying a production graph."),
    ToolRole("export_provenance", "Generate JSON, CSV, Turtle, and Markdown provenance."),
)


def tool_names() -> tuple[str, ...]:
    names = tuple(role.name for role in TOOL_REGISTRY)
    if names != TOOL_NAMES:
        raise RuntimeError("tool registry is not canonical")
    return names
