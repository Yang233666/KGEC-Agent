# Third-party notices

KGEC-Agent 1.0.0 directly depends on the following separately installed
packages. No dependency source code is vendored in this repository.

| Direct dependency | Validated version | Licence identifier | Use |
|---|---:|---|---|
| Pydantic | 2.13.4 | MIT | Validated schemas and structured provider output |
| RDFLib | 7.6.0 | BSD-3-Clause | RDF/PROV-O construction and Turtle validation |
| Streamlit | 1.50.0 | Apache-2.0 | Optional reviewer interface |
| pytest | 9.1.1 | MIT | Development and public-release tests |
| PyYAML | 6.0.3 | MIT | Development-time YAML validation |

The package manager resolves additional transitive dependencies for Streamlit.
Their installed metadata remains authoritative; this repository does not
redistribute their source.

No third-party source code, model weights, checkpoints, raw tensors, datasets,
RDF dumps, CEUR assets, fonts, or external calibrator code are redistributed.

`figures/architecture_workflow.png` was created for this public repository from
the implemented component and tool registry. The workflow composite and three
canonical decision screenshots, provenance screenshot, and video thumbnail are
KGEC-Agent project-generated demonstration assets. The composite and thumbnail
are derived only from the final running-application captures. Their hashes are
recorded in `release-manifest.json`. They depict deterministic synthetic
integration fixtures, not benchmark results or live-model output.
