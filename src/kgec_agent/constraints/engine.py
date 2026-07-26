"""Seven explicit semantic checks inspired by graph-validation principles."""

from __future__ import annotations

from collections.abc import Callable

from kgec_agent.schemas.models import (
    CONSTRAINT_CATEGORIES,
    Candidate,
    ConstraintCheck,
    ConstraintContext,
    SemanticResult,
    StructuredQuery,
)


class SemanticValidator:
    def _check(
        self,
        category: str,
        passed: bool,
        context: ConstraintContext,
        pass_detail: str,
        fail_detail: str,
    ) -> ConstraintCheck:
        status = "PASS" if passed else "VIOLATION"
        return ConstraintCheck(
            category=category,
            passed=passed,
            blocking=context.blocking_categories[category],
            reason_code=f"SEMANTIC_{category.upper()}_{status}",
            detail=pass_detail if passed else fail_detail,
        )

    def check_domain(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        del query, candidate
        return self._check(
            "domain",
            context.subject_type == context.expected_domain,
            context,
            "Subject type satisfies the relation domain.",
            "Subject type violates the relation domain.",
        )

    def check_range(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        del query
        return self._check(
            "range",
            candidate.entity_type == context.expected_range,
            context,
            "Candidate type satisfies the relation range.",
            "Candidate type violates the relation range.",
        )

    def check_entity_type(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        del query
        return self._check(
            "entity_type",
            candidate.entity_type in context.allowed_candidate_types,
            context,
            "Candidate has an explicitly allowed entity type.",
            "Candidate entity type is not allowed for this scenario.",
        )

    def check_duplicate(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        triple = (query.subject, query.relation, candidate.entity)
        return self._check(
            "duplicate",
            triple not in context.existing_triples,
            context,
            "Candidate triple is not already present.",
            "Candidate triple duplicates an existing statement.",
        )

    def check_contradiction(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        triple = (query.subject, query.relation, candidate.entity)
        return self._check(
            "contradiction",
            triple not in context.contradicting_triples,
            context,
            "No known contradictory statement was found.",
            "A known contradiction blocks this candidate.",
        )

    def check_functional_property(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        del query
        passed = (
            not context.functional_property
            or not context.existing_functional_objects
            or candidate.entity in context.existing_functional_objects
        )
        return self._check(
            "functional_property",
            passed,
            context,
            "Functional-property cardinality is satisfied.",
            "A different object already occupies this functional property.",
        )

    def check_inverse_relation(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> ConstraintCheck:
        expected = (
            candidate.entity,
            context.inverse_relation or "",
            query.subject,
        )
        passed = context.inverse_relation is None or expected in context.inverse_triples
        return self._check(
            "inverse_relation",
            passed,
            context,
            "Inverse-relation condition is satisfied.",
            "Required inverse-relation statement is missing.",
        )

    def check_semantic_constraints(
        self, query: StructuredQuery, candidate: Candidate, context: ConstraintContext
    ) -> SemanticResult:
        methods: dict[str, Callable[..., ConstraintCheck]] = {
            "domain": self.check_domain,
            "range": self.check_range,
            "entity_type": self.check_entity_type,
            "duplicate": self.check_duplicate,
            "contradiction": self.check_contradiction,
            "functional_property": self.check_functional_property,
            "inverse_relation": self.check_inverse_relation,
        }
        checks = [methods[name](query, candidate, context) for name in CONSTRAINT_CATEGORIES]
        blocking = [check.category for check in checks if not check.passed and check.blocking]
        reasons = [check.reason_code for check in checks]
        reasons.append(
            "SEMANTIC_BLOCKING_VIOLATION"
            if blocking
            else "SEMANTIC_CHECKS_NO_BLOCKING_VIOLATION"
        )
        return SemanticResult(
            checks=checks,
            blocking_violations=blocking,
            reason_codes=reasons,
        )
