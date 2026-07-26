import csv
import json

from rdflib import Graph
from rdflib.namespace import PROV, RDF

from kgec_agent.agent.replay import replay_scenario


def test_four_exports_parse_and_contain_required_fields(tmp_path):
    result = replay_scenario("canonical_verify_review", tmp_path)
    paths = result.export_paths
    assert set(paths) == {"json", "csv", "turtle", "markdown"}

    document = json.loads(open(paths["json"], encoding="utf-8").read())
    assert document["final_decision"] == "human_review"
    assert len(document["tool_invocations"]) == 8

    with open(paths["csv"], newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["evidence_outcome"] == "not_found"
    assert rows[0]["content_hash"] == result.run.content_hash

    graph = Graph()
    graph.parse(paths["turtle"], format="turtle")
    assert len(graph) > 20
    assert any(graph.triples((None, RDF.type, PROV.Activity)))
    assert any(graph.triples((None, PROV.wasAssociatedWith, None)))
    assert any(graph.triples((None, PROV.used, None)))
    assert any(graph.triples((None, PROV.generated, None)))

    markdown = open(paths["markdown"], encoding="utf-8").read()
    for required in (
        "Structured query",
        "Candidates",
        "Ordered tool invocations",
        "Semantic checks",
        "Final decision",
        "Content hash",
    ):
        assert required in markdown
