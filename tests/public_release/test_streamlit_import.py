import importlib.util
import json
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

from kgec_agent.agent.replay import available_scenarios, load_fixture


def test_streamlit_application_imports_without_torch_and_config_resolves():
    root = Path(__file__).resolve().parents[2]
    launcher = root / "apps" / "kgec_agent_demo.py"
    spec = importlib.util.spec_from_file_location("kgec_agent_demo", launcher)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert callable(module.run_app)
    assert "torch" not in sys.modules

    config = json.loads(
        (root / "configs" / "ui" / "default_ui_v1.json").read_text(encoding="utf-8")
    )
    assert config["network_enabled"] is False
    assert config["live_kge_enabled"] is False
    assert config["live_llm_enabled"] is False
    assert tuple(config["available_scenarios"]) == available_scenarios()
    for scenario in available_scenarios():
        assert load_fixture(scenario).scenario_id == scenario


def test_streamlit_default_session_executes():
    root = Path(__file__).resolve().parents[2]
    application = AppTest.from_file(
        str(root / "apps" / "kgec_agent_demo.py"),
        default_timeout=20,
    ).run()
    assert not application.exception
    assert application.title[0].value == "KGEC-Agent"
    assert application.selectbox[0].value == "canonical_accept"
    subheaders = [item.value for item in application.subheader]
    assert "Decision snapshot" in subheaders
    assert "Provenance trace and four-format export" in subheaders
