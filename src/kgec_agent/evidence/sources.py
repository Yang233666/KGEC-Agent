"""Offline local evidence and opt-in SPARQL evidence adapters."""

from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Protocol

from pydantic import AnyHttpUrl

from kgec_agent.schemas.models import Candidate, EvidenceFixture, EvidenceResult, StructuredQuery


class EvidenceSource(Protocol):
    def retrieve(self, query: StructuredQuery, candidate: Candidate) -> EvidenceResult: ...


class EvidenceSourceRegistry:
    def __init__(self) -> None:
        self._sources: dict[str, EvidenceSource] = {}

    def register(self, name: str, source: EvidenceSource) -> None:
        if name in self._sources:
            raise ValueError(f"evidence source already registered: {name}")
        self._sources[name] = source

    def get(self, name: str) -> EvidenceSource:
        try:
            return self._sources[name]
        except KeyError as exc:
            raise KeyError(f"unknown evidence source: {name}") from exc

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._sources))


class LocalEvidenceSource:
    def __init__(self, fixture: EvidenceFixture, *, required: bool) -> None:
        self.fixture = fixture
        self.required = required

    def retrieve(self, query: StructuredQuery, candidate: Candidate) -> EvidenceResult:
        del query, candidate
        if not self.required:
            return EvidenceResult(
                source="local_fixture",
                outcome="not_requested",
                detail="The initial route does not require evidence retrieval.",
                reason_codes=["EVIDENCE_NOT_REQUIRED"],
            )
        reason = {
            "supporting": "LOCAL_EVIDENCE_SUPPORTING",
            "contradicting": "LOCAL_EVIDENCE_CONTRADICTING",
            "not_found": "LOCAL_EVIDENCE_NOT_FOUND",
        }[self.fixture.outcome]
        return EvidenceResult(
            source="local_fixture",
            outcome=self.fixture.outcome,
            detail=self.fixture.detail,
            reason_codes=[reason],
        )


class SPARQLSourceConfig:
    def __init__(self, endpoint_url: str | AnyHttpUrl, timeout_seconds: float = 5.0) -> None:
        self.endpoint_url = str(AnyHttpUrl(str(endpoint_url)))
        if timeout_seconds <= 0 or timeout_seconds > 60:
            raise ValueError("timeout_seconds must be in (0, 60]")
        self.timeout_seconds = timeout_seconds


Transport = Callable[[urllib.request.Request, float], bytes]


def _default_transport(request: urllib.request.Request, timeout: float) -> bytes:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _iri(value: str) -> str:
    if not value.startswith(("https://", "http://", "urn:")):
        raise ValueError("SPARQL subjects, predicates, and candidates must be absolute IRIs")
    if any(character in value for character in "<>\"{}|\\^`"):
        raise ValueError("unsafe character in SPARQL IRI")
    return f"<{value}>"


class SPARQLEvidenceSource:
    """Configurable SPARQL JSON adapter; never selected by offline replay."""

    def __init__(self, config: SPARQLSourceConfig, transport: Transport | None = None) -> None:
        self.config = config
        self.transport = transport or _default_transport

    def build_query(self, query: StructuredQuery, candidate: Candidate) -> str:
        subject = _iri(query.subject)
        predicate = _iri(query.relation)
        object_ = _iri(candidate.entity)
        contradiction = _iri("https://w3id.org/kgec-agent/vocab#contradicts")
        return (
            "SELECT ?relation WHERE { "
            f"{{ {subject} {predicate} {object_} . BIND(\"supporting\" AS ?relation) }} "
            "UNION "
            f"{{ {subject} {contradiction} {object_} . BIND(\"contradicting\" AS ?relation) }} "
            "} LIMIT 1"
        )

    def retrieve(self, query: StructuredQuery, candidate: Candidate) -> EvidenceResult:
        sparql = self.build_query(query, candidate)
        request = urllib.request.Request(
            self.config.endpoint_url,
            data=urllib.parse.urlencode({"query": sparql}).encode("utf-8"),
            headers={"Accept": "application/sparql-results+json"},
            method="POST",
        )
        try:
            payload = self.transport(request, self.config.timeout_seconds)
        except (TimeoutError, socket.timeout):
            return EvidenceResult(
                source="sparql",
                outcome="unavailable",
                detail="SPARQL request timed out.",
                reason_codes=["SPARQL_TIMEOUT"],
            )
        except (urllib.error.URLError, OSError):
            return EvidenceResult(
                source="sparql",
                outcome="unavailable",
                detail="SPARQL endpoint was unavailable.",
                reason_codes=["SPARQL_ENDPOINT_UNAVAILABLE"],
            )
        try:
            document = json.loads(payload.decode("utf-8"))
            bindings = document["results"]["bindings"]
            if not bindings:
                outcome = "not_found"
            else:
                outcome = bindings[0]["relation"]["value"]
                if outcome not in {"supporting", "contradicting"}:
                    raise ValueError("unrecognized evidence relation")
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return EvidenceResult(
                source="sparql",
                outcome="error",
                detail="SPARQL response was malformed.",
                reason_codes=["SPARQL_MALFORMED_RESPONSE"],
            )
        return EvidenceResult(
            source="sparql",
            outcome=outcome,
            detail=f"SPARQL evidence outcome: {outcome}.",
            reason_codes=[f"SPARQL_{outcome.upper()}"],
        )
