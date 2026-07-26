"""Final decision rules; semantic blocking has authority over confidence."""

from kgec_agent.schemas.models import DecisionResult, EvidenceResult, PolicyResult, SemanticResult


class DecisionEngine:
    def make_final_decision(
        self,
        policy: PolicyResult,
        evidence: EvidenceResult,
        semantics: SemanticResult,
    ) -> DecisionResult:
        if semantics.blocking_violations:
            return DecisionResult(
                final_decision="rejected",
                destination="rejection_state",
                reason_codes=["REJECTED_BY_BLOCKING_CONSTRAINT", *semantics.blocking_violations],
            )
        if policy.initial_route == "auto_accept":
            return DecisionResult(
                final_decision="accepted",
                destination="accepted_candidate_graph",
                reason_codes=["ACCEPTED_AFTER_SEMANTIC_VALIDATION"],
            )
        if policy.initial_route == "verify":
            if evidence.outcome == "supporting":
                return DecisionResult(
                    final_decision="accepted",
                    destination="accepted_candidate_graph",
                    reason_codes=["ACCEPTED_AFTER_SUPPORTING_EVIDENCE"],
                )
            if evidence.outcome == "contradicting":
                return DecisionResult(
                    final_decision="rejected",
                    destination="rejection_state",
                    reason_codes=["REJECTED_BY_CONTRADICTING_EVIDENCE"],
                )
            return DecisionResult(
                final_decision="human_review",
                destination="human_review_queue",
                reason_codes=["HUMAN_REVIEW_AFTER_UNRESOLVED_EVIDENCE"],
            )
        return DecisionResult(
            final_decision="abstained",
            destination="abstention_state",
            reason_codes=["ABSTAINED_BELOW_VERIFY_THRESHOLD"],
        )
