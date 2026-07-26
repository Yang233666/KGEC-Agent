# KGEC-Agent Replay: `canonical_accept`

- Run identifier: `run-57991128775f5dbcb1089c9f`
- Implementation version: `1.0.0`
- Execution mode: `offline_fixture_replay`
- Natural-language request: Predict which entity is supported by h_person using r_supports.
- Structured query: `(h_person, r_supports, ?)`
- Confidence: `0.920000`
- Top-1/Top-2 margin: `0.860000`
- Thresholds: accept `0.85`, verify `0.5`, margin `0.1`
- Initial route: `auto_accept`
- Evidence outcome: `not_requested`
- Final decision: `accepted`
- Destination: `accepted_candidate_graph`
- Content hash: `ce83017d5a45165344482406dc5cdcfcb344c44638bbd2f15c41064600b48287`

## Candidates

| Rank | Entity | Raw score | Calibrated probability |
|---:|---|---:|---:|
| 1 | `t_supported` | 3.200000 | 0.920000 |
| 2 | `t_alternative` | 1.100000 | 0.060000 |
| 3 | `t_other` | 0.400000 | 0.020000 |

## Ordered tool invocations

| Order | Tool | Status | Input hash | Output hash |
|---:|---|---|---|---|
| 1 | `predict_link` | success | `a15eddb7ac4b7c61d4dec932b0a2bfdfe4707832bea1a1240b5d7c3fae0ae350` | `bfccef26eb4de1358913aa41fb9f9affd7bc9d708d2c6b110900bef538e11707` |
| 2 | `calibrate_prediction` | success | `bfccef26eb4de1358913aa41fb9f9affd7bc9d708d2c6b110900bef538e11707` | `780fe979dc32cc86f4bd633554485c3e59e7fd9f00afad3171ba07b32289975e` |
| 3 | `apply_confidence_policy` | success | `543b2918809e85e40a2edc10a32974a31e3366e91d55e7e9058e42bcc7e6027d` | `737d10fd8f5f7e5fb0e0726e1c327e978d80da38ee6d09edac8a1a71deca8685` |
| 4 | `retrieve_evidence` | success | `06e2d035cc336fe4f02a07bd9dc8b7c9b3af621c474578f61f7568fec8b720f0` | `ddc20dd0effc9feac8155b821f69cb2b0808cb1aa3c6041d396f19f1dec182d2` |
| 5 | `check_semantic_constraints` | success | `a7ae8b69816f6407869a45d8f02910214ac85e3d6cae40eabc1b50af6f2331f5` | `2c9fa2da7791eff3ff33267afee641b1b903b87187b76f3bdc40ba32e57929e7` |
| 6 | `make_final_decision` | success | `8ecedbd38e012abbb277d776000cc321ad03d08cb125b4942e5ea173a9ab2242` | `6ba354933fc38c645989d615b5bb8f305f78e86d834629bc5e1dd20cfc7ff2b3` |
| 7 | `propose_kg_update` | success | `bf38077374587711572f4b6dc3ee630d4693246e8b30bb98468a3446d95cc398` | `5b6c7a4946526b0309a098aae75429540de36cc7c4a658e867d144ffd853acef` |
| 8 | `export_provenance` | success | `386088200e295f68214bd285ddf94808a1b0ad3fffda09ba2a9e99ce5f0a8caf` | `0422f1fcab115b262878c3196576ae90ca40be65502d853bfe545c9e74296523` |

## Semantic checks

| Category | Passed | Blocking | Reason code |
|---|---|---|---|
| `domain` | True | True | `SEMANTIC_DOMAIN_PASS` |
| `range` | True | True | `SEMANTIC_RANGE_PASS` |
| `entity_type` | True | True | `SEMANTIC_ENTITY_TYPE_PASS` |
| `duplicate` | True | True | `SEMANTIC_DUPLICATE_PASS` |
| `contradiction` | True | True | `SEMANTIC_CONTRADICTION_PASS` |
| `functional_property` | True | True | `SEMANTIC_FUNCTIONAL_PROPERTY_PASS` |
| `inverse_relation` | True | True | `SEMANTIC_INVERSE_RELATION_PASS` |

## Reason codes

- `PREDICTION_FROM_REVIEWED_FIXTURE`
- `CALIBRATION_FROM_REVIEWED_FIXTURE`
- `TOP1_MARGIN_COMPUTED`
- `CONFIDENCE_ACCEPT_THRESHOLD_MET`
- `MARGIN_THRESHOLD_MET`
- `EVIDENCE_NOT_REQUIRED`
- `SEMANTIC_DOMAIN_PASS`
- `SEMANTIC_RANGE_PASS`
- `SEMANTIC_ENTITY_TYPE_PASS`
- `SEMANTIC_DUPLICATE_PASS`
- `SEMANTIC_CONTRADICTION_PASS`
- `SEMANTIC_FUNCTIONAL_PROPERTY_PASS`
- `SEMANTIC_INVERSE_RELATION_PASS`
- `SEMANTIC_CHECKS_NO_BLOCKING_VIOLATION`
- `ACCEPTED_AFTER_SEMANTIC_VALIDATION`
- `CANDIDATE_GRAPH_ONLY`

## Recorded explanation

canonical_accept routed to auto_accept; evidence was not_requested. The recorded final decision is accepted and the destination is accepted_candidate_graph.
