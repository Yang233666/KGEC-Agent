# Reproducibility

## Deterministic inputs

The authoritative public fixtures are packaged under
`src/kgec_agent/demo/fixtures/`. They record the natural-language request,
structured query, Top-k candidates, raw scores, calibrated probabilities,
policy thresholds, evidence result, semantic context, and expected outcome.

Run identifiers, event ordering, tool hashes, run content hashes, and all four
exports are deterministic for a given fixture and implementation version. No
wall-clock timestamp enters the serialized record.

## Full validation

```bash
python -m pip install '.[ui,dev]'
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/public_release
python scripts/validate_public_release.py
```

The test suite:

- replays all three scenarios;
- blocks socket/HTTP calls during replay;
- verifies exactly eight tools;
- tests policy boundaries;
- exercises seven independent semantic categories and blocking override;
- tests fixture and mocked live structured LLM providers;
- tests six SPARQL outcomes/failures with injected transports;
- parses JSON, CSV, Turtle, and Markdown;
- parses Turtle with RDFLib and checks PROV-O relations;
- compares repeated content and export hashes;
- imports the Streamlit launcher without PyTorch; and
- validates the complete manifest, denylist, private paths, placeholders,
  secrets, sizes, and checksums.

## Release integrity

`release-manifest.json` lists every intended file once. Its own digest is
canonical: the two fixed-width hash fields for the manifest and `SHA256SUMS`
are normalized to zeroes before hashing. `SHA256SUMS` excludes itself and uses
that canonical digest for its manifest line. The supplied validator implements
these rules and verifies every ordinary file by raw SHA-256.

## Limitations

- Only deterministic fixtures are included; no benchmark dataset or model
  weights are redistributed.
- The validated clean room uses Python 3.12 on arm64 macOS. CI declares the
  same Python minor version on Linux.
- Live LLM and SPARQL tests use mocked transports; no public endpoint is called.
- The optional real-model protocol has no bundled adapter.
- Screenshots are captured from the running reviewer interface and disclose
  that the displayed workflows are deterministic synthetic integration
  fixtures.
