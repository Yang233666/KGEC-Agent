# Architecture

![KGEC-Agent architecture](../figures/architecture_workflow.png)

## Authority and data flow

The orchestration provider maps a natural-language request to a
`StructuredQuery` and the canonical tool plan. Pydantic rejects unknown or
malformed fields. The provider does not receive authority to alter prediction
scores, calibrated probabilities, thresholds, semantic checks, final
decisions, or destinations.

The replay engine invokes these roles in a fixed order:

1. `predict_link`
2. `calibrate_prediction`
3. `apply_confidence_policy`
4. `retrieve_evidence`
5. `check_semantic_constraints`
6. `make_final_decision`
7. `propose_kg_update`
8. `export_provenance`

Each invocation records a status, canonical input hash, output hash, event
order, and reason codes.

## Offline boundary

The fixture prediction and calibration services consume packaged JSON. They do
not import PyTorch, an external calibrator, embeddings, checkpoints, or raw
tensors. `RealModelAdapter` is a lazy protocol and imports an implementation
only when an explicit integration path is supplied.

The evidence registry contains the local fixture source in replay. The SPARQL
class exists as an opt-in adapter but is never registered or instantiated by
the default engine.

## Decision boundary

Confidence and margin determine only the initial route. Any blocking semantic
violation yields rejection before accepted candidate staging. Accepted output
is a candidate-graph proposal; the implementation contains no production
graph writer.
