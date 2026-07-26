"""Unified deterministic JSON, CSV, PROV-O Turtle, and Markdown exporter."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import PROV, RDF, XSD

from kgec_agent.schemas.models import RunRecord


KGEC = Namespace("https://w3id.org/kgec-agent/vocab#")
RESOURCE = "https://w3id.org/kgec-agent/resource/"


class ProvenanceExporter:
    formats = ("json", "csv", "turtle", "markdown")

    def export_all(self, run: RunRecord, output_dir: Path) -> dict[str, Path]:
        output_dir = Path(output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        serializers = {
            "json": (self.to_json(run), ".json"),
            "csv": (self.to_csv(run), ".csv"),
            "turtle": (self.to_turtle(run), ".ttl"),
            "markdown": (self.to_markdown(run), ".md"),
        }
        paths: dict[str, Path] = {}
        for name, (content, suffix) in serializers.items():
            path = output_dir / f"{run.scenario_id}{suffix}"
            path.write_text(content, encoding="utf-8", newline="\n")
            paths[name] = path
        return paths

    def to_json(self, run: RunRecord) -> str:
        return json.dumps(run.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"

    def to_csv(self, run: RunRecord) -> str:
        buffer = io.StringIO(newline="")
        fields = [
            "run_id",
            "scenario_id",
            "implementation_version",
            "structured_query",
            "candidates",
            "raw_scores",
            "calibrated_probabilities",
            "confidence",
            "margin",
            "thresholds",
            "initial_route",
            "tool_invocations",
            "reason_codes",
            "evidence_outcome",
            "semantic_checks",
            "final_decision",
            "destination",
            "stable_event_order",
            "content_hash",
        ]
        writer = csv.DictWriter(buffer, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "run_id": run.run_id,
                "scenario_id": run.scenario_id,
                "implementation_version": run.implementation_version,
                "structured_query": json.dumps(run.structured_query.model_dump(mode="json"), sort_keys=True),
                "candidates": json.dumps([item.model_dump(mode="json") for item in run.candidates], sort_keys=True),
                "raw_scores": json.dumps(run.raw_scores),
                "calibrated_probabilities": json.dumps(run.calibrated_probabilities),
                "confidence": run.confidence,
                "margin": run.margin,
                "thresholds": json.dumps(run.thresholds.model_dump(mode="json"), sort_keys=True),
                "initial_route": run.initial_route,
                "tool_invocations": json.dumps([item.model_dump(mode="json") for item in run.tool_invocations], sort_keys=True),
                "reason_codes": json.dumps(run.reason_codes),
                "evidence_outcome": run.evidence.outcome,
                "semantic_checks": json.dumps([item.model_dump(mode="json") for item in run.semantic_checks], sort_keys=True),
                "final_decision": run.final_decision,
                "destination": run.destination,
                "stable_event_order": json.dumps(run.stable_event_order),
                "content_hash": run.content_hash,
            }
        )
        return buffer.getvalue()

    def to_turtle(self, run: RunRecord) -> str:
        graph = Graph()
        run_uri = URIRef(f"{RESOURCE}run/{run.run_id}")
        agent_uri = URIRef(f"{RESOURCE}agent/kgec-agent-{run.implementation_version}")
        query_uri = URIRef(f"{RESOURCE}query/{run.run_id}")
        evidence_uri = URIRef(f"{RESOURCE}evidence/{run.run_id}")
        decision_uri = URIRef(f"{RESOURCE}decision/{run.run_id}")

        graph.add((run_uri, RDF.type, PROV.Activity))
        graph.add((run_uri, PROV.wasAssociatedWith, agent_uri))
        graph.add((run_uri, KGEC.scenarioIdentifier, Literal(run.scenario_id)))
        graph.add((run_uri, KGEC.contentHash, Literal(run.content_hash)))
        graph.add((agent_uri, RDF.type, PROV.Agent))
        graph.add((agent_uri, KGEC.implementationVersion, Literal(run.implementation_version)))
        graph.add((query_uri, RDF.type, PROV.Entity))
        graph.add((query_uri, KGEC.subject, Literal(run.structured_query.subject)))
        graph.add((query_uri, KGEC.relation, Literal(run.structured_query.relation)))
        graph.add((run_uri, PROV.used, query_uri))

        for index, candidate in enumerate(run.candidates, start=1):
            candidate_uri = URIRef(f"{RESOURCE}candidate/{run.run_id}/{index}")
            graph.add((candidate_uri, RDF.type, PROV.Entity))
            graph.add((candidate_uri, KGEC.entityIdentifier, Literal(candidate.entity)))
            graph.add((candidate_uri, KGEC.rawScore, Literal(candidate.raw_score, datatype=XSD.double)))
            graph.add(
                (
                    candidate_uri,
                    KGEC.calibratedProbability,
                    Literal(candidate.calibrated_probability, datatype=XSD.double),
                )
            )
            graph.add((run_uri, PROV.generated, candidate_uri))

        graph.add((evidence_uri, RDF.type, PROV.Entity))
        graph.add((evidence_uri, KGEC.evidenceOutcome, Literal(run.evidence.outcome)))
        graph.add((run_uri, PROV.generated, evidence_uri))
        graph.add((decision_uri, RDF.type, PROV.Entity))
        graph.add((decision_uri, KGEC.finalDecision, Literal(run.final_decision)))
        graph.add((decision_uri, KGEC.destination, Literal(run.destination)))
        graph.add((run_uri, PROV.generated, decision_uri))

        previous_activity: URIRef | None = None
        for invocation in run.tool_invocations:
            tool_uri = URIRef(f"{RESOURCE}tool/{run.run_id}/{invocation.order}")
            state_uri = URIRef(f"{RESOURCE}state/{run.run_id}/{invocation.order}")
            graph.add((tool_uri, RDF.type, PROV.Activity))
            graph.add((tool_uri, PROV.wasAssociatedWith, agent_uri))
            graph.add((tool_uri, PROV.used, query_uri))
            graph.add((tool_uri, KGEC.toolName, Literal(invocation.tool_name)))
            graph.add((tool_uri, KGEC.inputHash, Literal(invocation.input_hash)))
            if invocation.output_hash:
                graph.add((tool_uri, KGEC.outputHash, Literal(invocation.output_hash)))
            if previous_activity is not None:
                graph.add((tool_uri, PROV.wasInformedBy, previous_activity))
            graph.add((state_uri, RDF.type, PROV.Entity))
            graph.add((state_uri, KGEC.eventOrder, Literal(invocation.order, datatype=XSD.integer)))
            graph.add((tool_uri, PROV.generated, state_uri))
            graph.add((run_uri, PROV.used, state_uri))
            for reason in invocation.reason_codes:
                graph.add((state_uri, KGEC.reasonCode, Literal(reason)))
            previous_activity = tool_uri

        prefix_lines = [
            "@prefix kgec: <https://w3id.org/kgec-agent/vocab#> .",
            "@prefix prov: <http://www.w3.org/ns/prov#> .",
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
            "",
        ]
        triples = sorted(
            f"{subject.n3()} {predicate.n3()} {object_.n3()} ."
            for subject, predicate, object_ in graph
        )
        return "\n".join([*prefix_lines, *triples, ""])

    def to_markdown(self, run: RunRecord) -> str:
        candidates = "\n".join(
            f"| {index} | `{item.entity}` | {item.raw_score:.6f} | {item.calibrated_probability:.6f} |"
            for index, item in enumerate(run.candidates, start=1)
        )
        tools = "\n".join(
            f"| {item.order} | `{item.tool_name}` | {item.status} | `{item.input_hash}` | `{item.output_hash}` |"
            for item in run.tool_invocations
        )
        checks = "\n".join(
            f"| `{item.category}` | {item.passed} | {item.blocking} | `{item.reason_code}` |"
            for item in run.semantic_checks
        )
        return f"""# KGEC-Agent Replay: `{run.scenario_id}`

- Run identifier: `{run.run_id}`
- Implementation version: `{run.implementation_version}`
- Execution mode: `{run.execution_mode}`
- Natural-language request: {run.natural_language_request}
- Structured query: `({run.structured_query.subject}, {run.structured_query.relation}, ?)`
- Confidence: `{run.confidence:.6f}`
- Top-1/Top-2 margin: `{run.margin:.6f}`
- Thresholds: accept `{run.thresholds.accept_threshold}`, verify `{run.thresholds.verify_threshold}`, margin `{run.thresholds.margin_threshold}`
- Initial route: `{run.initial_route}`
- Evidence outcome: `{run.evidence.outcome}`
- Final decision: `{run.final_decision}`
- Destination: `{run.destination}`
- Content hash: `{run.content_hash}`

## Candidates

| Rank | Entity | Raw score | Calibrated probability |
|---:|---|---:|---:|
{candidates}

## Ordered tool invocations

| Order | Tool | Status | Input hash | Output hash |
|---:|---|---|---|---|
{tools}

## Semantic checks

| Category | Passed | Blocking | Reason code |
|---|---|---|---|
{checks}

## Reason codes

{chr(10).join(f"- `{reason}`" for reason in run.reason_codes)}

## Recorded explanation

{run.llm_explanation}
"""
