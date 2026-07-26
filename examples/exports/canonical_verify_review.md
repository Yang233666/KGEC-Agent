# KGEC-Agent Replay: `canonical_verify_review`

- Run identifier: `run-c7338f408e2cc3f0c159caea`
- Implementation version: `1.0.0`
- Execution mode: `offline_fixture_replay`
- Natural-language request: Review the most likely tail for h_person using r_review.
- Structured query: `(h_person, r_review, ?)`
- Confidence: `0.720000`
- Top-1/Top-2 margin: `0.560000`
- Thresholds: accept `0.85`, verify `0.5`, margin `0.1`
- Initial route: `verify`
- Evidence outcome: `not_found`
- Final decision: `human_review`
- Destination: `human_review_queue`
- Content hash: `6ee3becfd5e190a28f1d7381f3a3ff737c26c675ec8db5ad6a23703a40a59b01`

## Candidates

| Rank | Entity | Raw score | Calibrated probability |
|---:|---|---:|---:|
| 1 | `t_review` | 2.100000 | 0.720000 |
| 2 | `t_review_alt` | 1.200000 | 0.160000 |
| 3 | `t_review_other` | 0.900000 | 0.120000 |

## Ordered tool invocations

| Order | Tool | Status | Input hash | Output hash |
|---:|---|---|---|---|
| 1 | `predict_link` | success | `b971cb43ed41560f7a7de8a1f003ae498789b2b6ce6451c5ad751e660f02bee1` | `e5bf54ba8cd0922bb4587b98b380ab41f1b3f44eabf8725ccd503ad687ec2046` |
| 2 | `calibrate_prediction` | success | `e5bf54ba8cd0922bb4587b98b380ab41f1b3f44eabf8725ccd503ad687ec2046` | `90ed546059b54db4e8c7961fda37de2bd3778a8b3635d5fd651fc874a796da79` |
| 3 | `apply_confidence_policy` | success | `84d0c94eb348e9f06feeb5a7ec1a7e6dc738d547eee17bf99db8a3a62995c7a4` | `e0a0df97d94746133c6a31f55f728332a65aa3116494cde1f2752e09024ad939` |
| 4 | `retrieve_evidence` | success | `ca0b17c9b49e20de685d56595d999b88c098c5a2ad53ecec3e2b80abfa0fd565` | `84147f53a8a4e0efffc26f7cdaeb88ff551d8a5ee2b771fe7cf7fe2035e8729f` |
| 5 | `check_semantic_constraints` | success | `412de98193cbefcdee2eddd5fe1b63bf6d16324ab264f39b470989be39165de9` | `2c9fa2da7791eff3ff33267afee641b1b903b87187b76f3bdc40ba32e57929e7` |
| 6 | `make_final_decision` | success | `6107cf638a7460d2df76139717e525dc09315021ad75d266190e45d518a3f4cd` | `05693102fa576bc289ad98395395a09c2ed391c34c542ae1e6b11162b4c0566f` |
| 7 | `propose_kg_update` | success | `d4fca9e52a293cb52d54a56d2e926efc424ab1aecbd93d96ac9200c9ebf52179` | `2b8d8b0843e0d36e40b9657f010505fd434030477d75a43a82b3d190c7683fa9` |
| 8 | `export_provenance` | success | `c6fda7a8ba5d795f3a1a8f40b9d8e53f045b7f7ac3c55a0acc8507f9927d62ba` | `2ac7e47a79f3519ff759e94ffd552e3e0bf51c59b7d7d42b3d51def544c891bf` |

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
- `CONFIDENCE_VERIFY_REGION`
- `LOCAL_EVIDENCE_NOT_FOUND`
- `SEMANTIC_DOMAIN_PASS`
- `SEMANTIC_RANGE_PASS`
- `SEMANTIC_ENTITY_TYPE_PASS`
- `SEMANTIC_DUPLICATE_PASS`
- `SEMANTIC_CONTRADICTION_PASS`
- `SEMANTIC_FUNCTIONAL_PROPERTY_PASS`
- `SEMANTIC_INVERSE_RELATION_PASS`
- `SEMANTIC_CHECKS_NO_BLOCKING_VIOLATION`
- `HUMAN_REVIEW_AFTER_UNRESOLVED_EVIDENCE`
- `CANDIDATE_GRAPH_ONLY`

## Recorded explanation

canonical_verify_review routed to verify; evidence was not_found. The recorded final decision is human_review and the destination is human_review_queue.
