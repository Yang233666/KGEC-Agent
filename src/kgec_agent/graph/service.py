"""Candidate-routing service; never writes to a production knowledge graph."""

from kgec_agent.schemas.models import (
    Candidate,
    DecisionResult,
    GraphUpdateResult,
    StructuredQuery,
)


class CandidateGraphService:
    _OPERATIONS = {
        "accepted": "stage_candidate",
        "human_review": "route_for_review",
        "rejected": "record_rejection",
        "abstained": "record_abstention",
    }

    def propose_kg_update(
        self,
        query: StructuredQuery,
        candidate: Candidate,
        decision: DecisionResult,
    ) -> GraphUpdateResult:
        if query.direction == "tail":
            triple = (query.subject, query.relation, candidate.entity)
        else:
            triple = (candidate.entity, query.relation, query.subject)
        return GraphUpdateResult(
            operation=self._OPERATIONS[decision.final_decision],
            destination=decision.destination,
            candidate_triple=triple,
            reason_codes=["CANDIDATE_GRAPH_ONLY", *decision.reason_codes],
        )
