"""Streamlit reviewer interface for the offline fixture replay."""

from __future__ import annotations

from html import escape
import tempfile
from pathlib import Path

from kgec_agent import __version__
from kgec_agent.agent.replay import available_scenarios, load_fixture, replay_scenario


def _render_trace_table(st, run) -> None:
    rows = []
    for invocation in run.tool_invocations:
        rows.append(
            "<tr>"
            f"<td>{invocation.order}</td>"
            f"<td><strong>{escape(invocation.tool_name)}</strong></td>"
            f"<td>{escape(invocation.status)}</td>"
            f"<td><code>{escape(invocation.input_hash)}</code></td>"
            f"<td><code>{escape(invocation.output_hash)}</code></td>"
            "</tr>"
        )
    st.markdown(
        """
        <style>
          .kgec-trace-table {
            border-collapse: collapse;
            width: 100%;
            font-size: 0.72rem;
            line-height: 1.15;
          }
          .kgec-trace-table th,
          .kgec-trace-table td {
            border-bottom: 1px solid #d7dce2;
            padding: 0.28rem 0.38rem;
            text-align: left;
            vertical-align: top;
          }
          .kgec-trace-table code {
            font-size: 0.62rem;
            overflow-wrap: anywhere;
            word-break: break-all;
          }
        </style>
        <table class="kgec-trace-table">
          <thead>
            <tr>
              <th>#</th><th>Tool</th><th>Status</th>
              <th>Input SHA-256</th><th>Output SHA-256</th>
            </tr>
          </thead>
          <tbody>
        """
        + "".join(rows)
        + """
          </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )


def run_app() -> None:
    import streamlit as st

    st.set_page_config(page_title="KGEC-Agent", layout="wide")
    st.markdown(
        """
        <style>
          [data-testid="stHeader"],
          [data-testid="stToolbar"] {
            display: none;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("KGEC-Agent")
    st.caption(
        "Calibration-guided routing, evidence retrieval, semantic validation, "
        "candidate-graph staging, and inspectable provenance."
    )
    st.info(
        "Default mode is a deterministic CPU-only fixture replay. It makes no network "
        "request and performs no live KGE or LLM inference."
    )

    scenario_id = st.selectbox("Canonical scenario", available_scenarios())
    fixture = load_fixture(scenario_id)
    natural_request = st.text_area(
        "Natural-language request",
        value=fixture.natural_language_request,
        height=80,
    )
    if st.button("Run offline replay", type="primary") or "replay_result" not in st.session_state:
        output_dir = Path(tempfile.mkdtemp(prefix="kgec-agent-ui-"))
        try:
            st.session_state.replay_result = replay_scenario(
                scenario_id,
                output_dir,
                natural_language_request=natural_request,
            )
        except Exception as exc:
            st.error(f"Replay failed: {exc}")
            return

    result = st.session_state.replay_result
    run = result.run
    st.subheader("Decision snapshot")
    st.caption(
        f"Application version {__version__} · Scenario {run.scenario_id} · "
        "Deterministic synthetic integration fixture"
    )
    st.markdown("**Structured link-prediction query**")
    st.code(
        f"({run.structured_query.subject}, {run.structured_query.relation}, ?)"
        if run.structured_query.direction == "tail"
        else f"(?, {run.structured_query.relation}, {run.structured_query.subject})"
    )

    candidate_column, outcome_column = st.columns([1.15, 1])
    with candidate_column:
        st.markdown("**Top-k candidates and calibration**")
        st.dataframe(
            [
                {
                    "rank": index,
                    "entity": candidate.entity,
                    "type": candidate.entity_type,
                    "raw score": candidate.raw_score,
                    "calibrated probability": candidate.calibrated_probability,
                }
                for index, candidate in enumerate(run.candidates, start=1)
            ],
            width="stretch",
            hide_index=True,
            height=150,
        )
        metric_columns = st.columns(2)
        metric_columns[0].metric("Top-1 confidence", f"{run.confidence:.3f}")
        metric_columns[1].metric("Top-1/Top-2 margin", f"{run.margin:.3f}")

    passing_checks = sum(item.passed for item in run.semantic_checks)
    blocking_violations = [
        item for item in run.semantic_checks if item.blocking and not item.passed
    ]
    with outcome_column:
        st.markdown("**Policy, evidence, and semantic outcome**")
        st.markdown(
            "**Thresholds:** "
            f"accept `{run.thresholds.accept_threshold:.3f}` · "
            f"verify `{run.thresholds.verify_threshold:.3f}` · "
            f"margin `{run.thresholds.margin_threshold:.3f}`"
        )
        st.markdown(f"**Initial route:** `{run.initial_route}`")
        st.markdown(f"**Local evidence outcome:** `{run.evidence.outcome}`")
        st.markdown(
            f"**Semantic checks passing:** `{passing_checks}/{len(run.semantic_checks)}`"
        )
        if blocking_violations:
            violation_text = " · ".join(
                f"{item.category} — {item.reason_code}" for item in blocking_violations
            )
            st.error(f"Blocking semantic violation: {violation_text}")
        else:
            st.success("Blocking semantic violations: none")
        st.markdown(f"**Final decision:** `{run.final_decision}`")
        st.markdown(f"**Destination:** `{run.destination}`")

    st.divider()
    st.subheader("Provenance trace and four-format export")
    st.caption(f"Run content SHA-256: {run.content_hash}")
    _render_trace_table(st, run)
    st.markdown("**Reason codes**")
    st.caption(" · ".join(run.reason_codes))

    export_columns = st.columns(4)
    for column, name in zip(
        export_columns, ("json", "csv", "turtle", "markdown"), strict=True
    ):
        path = Path(result.export_paths[name])
        with column:
            st.download_button(
                label=f"Download {name.upper()}",
                data=path.read_bytes(),
                file_name=path.name,
                mime={
                    "json": "application/json",
                    "csv": "text/csv",
                    "turtle": "text/turtle",
                    "markdown": "text/markdown",
                }[name],
                key=f"download-{name}",
                width="stretch",
            )

    with st.expander("Detailed evidence, semantic checks, and explanation"):
        st.markdown("**Evidence result**")
        st.json(run.evidence.model_dump(mode="json"))
        st.markdown("**Semantic checks**")
        st.dataframe(
            [item.model_dump(mode="json") for item in run.semantic_checks],
            width="stretch",
            hide_index=True,
        )
        st.markdown("**Recorded explanation**")
        st.write(run.llm_explanation)

    with st.expander("Optional live integrations"):
        st.write(
            "Live structured LLM and SPARQL adapters are opt-in. They are never "
            "instantiated by this interface's default offline mode."
        )
