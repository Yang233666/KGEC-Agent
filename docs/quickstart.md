# Quick Start

## Requirements

- Python 3.11, 3.12, or 3.13
- CPU-only execution is sufficient
- no GPU, model weights, dataset, API key, or network connection for replay

The validated environment used Python 3.12 with the exact direct versions in
`requirements-demo.txt`.

## Install

From the repository root:

```bash
KGEC_AGENT_ENV="${TMPDIR:-/tmp}/kgec-agent-venv"
KGEC_AGENT_OUTPUT="${TMPDIR:-/tmp}/kgec-agent-output"
python3 -m venv "$KGEC_AGENT_ENV"
. "$KGEC_AGENT_ENV/bin/activate"
python -m pip install -r requirements-demo.txt
python -m pip install --no-deps .
```

## Replay

```bash
python -m kgec_agent.demo replay \
  --scenario canonical_accept \
  --output-dir "$KGEC_AGENT_OUTPUT/canonical_accept"
```

Expected summary fields are:

```text
SCENARIO=canonical_accept
FINAL_DECISION=accepted
DESTINATION=accepted_candidate_graph
RUN_HASH=<64 hexadecimal characters>
```

Four generated paths follow. The exact run hash is stable for version 1.0.0.

## Interface

```bash
streamlit run apps/kgec_agent_demo.py
```

Select one of the three scenarios and choose **Run offline replay**. The
interface runs only the packaged fixture provider and local evidence source.

## Common failures

- `unknown scenario`: use one of the three identifiers listed in `README.md`.
- `offline fixture mode accepts the reviewed scenario request only`: restore
  the selected scenario's displayed request.
- output permission error: choose another writable `--output-dir`.
- missing Streamlit: install `requirements-demo.txt`.
