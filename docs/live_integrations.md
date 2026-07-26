# Optional Live Integrations

Offline replay is the default and requires neither integration.

## Live structured LLM provider

`LiveStructuredLLMProvider` implements an OpenAI-compatible structured-output
request path. It reads settings only when explicitly constructed:

| Environment variable | Purpose |
|---|---|
| `KGEC_LLM_ENDPOINT` | Explicit structured-provider endpoint |
| `KGEC_LLM_MODEL` | Provider model identifier |
| `KGEC_LLM_API_KEY` | Runtime credential; never stored in this repository |
| `KGEC_LLM_TIMEOUT_SECONDS` | Bounded request timeout; default 20 seconds |

Responses are validated against Pydantic with unknown fields forbidden. A
malformed response raises a public provider-response error. Network and timeout
failures raise provider-unavailable errors. The LLM output is limited to a
structured query, canonical tool plan, or explanation string; system tools
remain authoritative for all numerical and admission fields.

## SPARQL evidence provider

`SPARQLEvidenceSource` takes an explicit endpoint and timeout, constructs a
bounded query for absolute IRIs, requests SPARQL JSON, and returns one of:
`supporting`, `contradicting`, `not_found`, `unavailable`, or `error`.

The adapter has no credential field. Deployments needing authenticated SPARQL
must inject transport-level authentication outside this repository. The public
tests inject local mock transports for supporting, contradicting, not-found,
timeout, malformed-response, and endpoint-failure cases.

## Safety

- Neither live class is instantiated by `ReplayEngine`.
- The Streamlit default has no live-mode selector.
- No default endpoint or credential is embedded.
- Live responses cannot modify recorded tool outputs.
- External failures are explicit and do not silently fabricate evidence.
