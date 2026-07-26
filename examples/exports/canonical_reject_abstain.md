# KGEC-Agent Replay: `canonical_reject_abstain`

- Run identifier: `run-08166fd932e3688c1e08110f`
- Implementation version: `1.0.0`
- Execution mode: `offline_fixture_replay`
- Natural-language request: Predict the tail for h_person using r_domain_bad.
- Structured query: `(h_person, r_domain_bad, ?)`
- Confidence: `0.910000`
- Top-1/Top-2 margin: `0.860000`
- Thresholds: accept `0.85`, verify `0.5`, margin `0.1`
- Initial route: `auto_accept`
- Evidence outcome: `not_requested`
- Final decision: `rejected`
- Destination: `rejection_state`
- Content hash: `3bb462244b9a7b78e84d66baa6e812c9bb2dd6d620be38b070e722f7a9243988`

## Candidates

| Rank | Entity | Raw score | Calibrated probability |
|---:|---|---:|---:|
| 1 | `t_domain_bad` | 3.400000 | 0.910000 |
| 2 | `t_domain_alt` | 1.000000 | 0.050000 |
| 3 | `t_domain_other` | 0.300000 | 0.040000 |

## Ordered tool invocations

| Order | Tool | Status | Input hash | Output hash |
|---:|---|---|---|---|
| 1 | `predict_link` | success | `c8342c515e8e97f3d13e86695f761720da95529a039b561301d653214501e1fc` | `d2f856c3ee52b0bcae1c90351035189903215ffb04ba9f1769917096363f8462` |
| 2 | `calibrate_prediction` | success | `d2f856c3ee52b0bcae1c90351035189903215ffb04ba9f1769917096363f8462` | `960faba9b8f12fc2ee92d9f635337aeeef28e933d2241dceb1658cdc015b0a63` |
| 3 | `apply_confidence_policy` | success | `f785ddb7481fe48830655e15657e947f3e9e0e704eb5cf528f1f6abf9024ee0e` | `15b3b8091d2b62155593c8de400d03f9ec7fd56825391ac7aa4356dab911903c` |
| 4 | `retrieve_evidence` | success | `bc4ccdd046fd56b79fc7a9ff6d899a43e71556475e6f89491bf7f93a32b4494b` | `ddc20dd0effc9feac8155b821f69cb2b0808cb1aa3c6041d396f19f1dec182d2` |
| 5 | `check_semantic_constraints` | success | `c6d28ac021daee307776f74de2a1b91cae0160e947d8ece7007c290b3894b4bf` | `a0314a8fbc15aa731a542df24cf409c6e630abb625e15ba92aa9a886cdcdab8f` |
| 6 | `make_final_decision` | success | `81513d98fb4d16293c3bfd2afabbf465b5bca008dabb0123f67811d9e64e6c8c` | `6bdf584f3b28dbd938e46bc12486a4c92e0a33493e0152f6991ccb5156e44475` |
| 7 | `propose_kg_update` | success | `ad5108ad3e99afabb375a90f596e3bb45b5a72df2d48b542eac0127f14111d8a` | `59ddefdd1b168796101c58f89bf031c7d1450c00c55864516e9ba4130283c8f7` |
| 8 | `export_provenance` | success | `432b550fc535306ea5b29530bec65236f211cc3e7df60474b685830ad70357ca` | `b7db50846dfea17df6c17fe72ac9341b04a9971cd042c77551298de77660fe11` |

## Semantic checks

| Category | Passed | Blocking | Reason code |
|---|---|---|---|
| `domain` | False | True | `SEMANTIC_DOMAIN_VIOLATION` |
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
- `SEMANTIC_DOMAIN_VIOLATION`
- `SEMANTIC_RANGE_PASS`
- `SEMANTIC_ENTITY_TYPE_PASS`
- `SEMANTIC_DUPLICATE_PASS`
- `SEMANTIC_CONTRADICTION_PASS`
- `SEMANTIC_FUNCTIONAL_PROPERTY_PASS`
- `SEMANTIC_INVERSE_RELATION_PASS`
- `SEMANTIC_BLOCKING_VIOLATION`
- `REJECTED_BY_BLOCKING_CONSTRAINT`
- `domain`
- `CANDIDATE_GRAPH_ONLY`

## Recorded explanation

canonical_reject_abstain routed to auto_accept; evidence was not_requested. The recorded final decision is rejected and the destination is rejection_state.
