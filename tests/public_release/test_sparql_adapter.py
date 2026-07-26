import json
import urllib.error

import pytest

from kgec_agent.evidence.sources import SPARQLEvidenceSource, SPARQLSourceConfig
from kgec_agent.schemas.models import Candidate, StructuredQuery


QUERY = StructuredQuery(
    subject="https://example.org/subject",
    relation="https://example.org/relation",
    direction="tail",
    top_k=3,
    natural_language="test",
)
CANDIDATE = Candidate(
    entity="https://example.org/object",
    label="Object",
    entity_type="Thing",
    raw_score=1.0,
    calibrated_probability=0.8,
)
CONFIG = SPARQLSourceConfig("https://example.invalid/sparql", timeout_seconds=1)


def payload(value=None):
    bindings = [] if value is None else [{"relation": {"type": "literal", "value": value}}]
    return json.dumps({"results": {"bindings": bindings}}).encode("utf-8")


@pytest.mark.parametrize(
    ("value", "expected"),
    [("supporting", "supporting"), ("contradicting", "contradicting"), (None, "not_found")],
)
def test_sparql_normalized_outcomes(value, expected):
    source = SPARQLEvidenceSource(CONFIG, transport=lambda request, timeout: payload(value))
    result = source.retrieve(QUERY, CANDIDATE)
    assert result.outcome == expected
    assert "SELECT ?relation" in source.build_query(QUERY, CANDIDATE)


def test_sparql_timeout():
    def timeout(request, seconds):
        raise TimeoutError

    result = SPARQLEvidenceSource(CONFIG, transport=timeout).retrieve(QUERY, CANDIDATE)
    assert result.outcome == "unavailable"
    assert result.reason_codes == ["SPARQL_TIMEOUT"]


def test_sparql_malformed_response():
    result = SPARQLEvidenceSource(
        CONFIG, transport=lambda request, timeout: b"not-json"
    ).retrieve(QUERY, CANDIDATE)
    assert result.outcome == "error"


def test_sparql_endpoint_failure():
    def failure(request, timeout):
        raise urllib.error.URLError("offline")

    result = SPARQLEvidenceSource(CONFIG, transport=failure).retrieve(QUERY, CANDIDATE)
    assert result.outcome == "unavailable"
    assert result.reason_codes == ["SPARQL_ENDPOINT_UNAVAILABLE"]
