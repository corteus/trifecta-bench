"""Adapter tests (SPEC-CORTEUS-TRIFECTA-BENCH-001): inputs never leak our labels,
and each parser reads the checker's real output saved in results/raw."""
import json
from pathlib import Path

import pytest

from bench.adapters import ltlint, mcp_trifecta, trifecta_check, triflow
from bench.score import scenario_tools

ROOT = Path(__file__).resolve().parent.parent
SERVERS = {p.stem: json.loads(p.read_text()) for p in (ROOT / "data" / "servers").glob("*.json")}
SCENARIOS = {s["id"]: s for s in json.loads((ROOT / "data" / "scenarios.json").read_text())}
CONFIGS = json.loads((ROOT / "data" / "server_configs.json").read_text())
ADAPTERS = {"lethal-trifecta-lint": ltlint, "mcp-trifecta": mcp_trifecta, "triflow": triflow, "trifecta-check": trifecta_check}


def tools(scenario_id):
    return scenario_tools(SCENARIOS[scenario_id], SERVERS)


@pytest.mark.parametrize("name", sorted(ADAPTERS))
@pytest.mark.parametrize("scenario_id", ["github-alone", "filesystem-fetch"])
def test_inputs_never_contain_our_labels_or_reasons(name, scenario_id):
    plan = ADAPTERS[name].build_input(tools(scenario_id), CONFIGS)
    text = " ".join(plan["files"].values())
    for doc in map(json.loads, plan["files"].values()):
        entries = doc.get("tools") or [t for server in doc.get("servers", []) for t in server["tools"]]
        for entry in entries:
            assert set(entry) <= {"name", "description", "inputSchema"}, entry.keys()
    for tool in tools(scenario_id):
        for reason in tool["reasons"].values():
            assert reason not in text
    assert "lethal trifecta" not in text.lower()
    assert plan["argv"] and all(isinstance(a, str) for a in plan["argv"])
    for path in plan["argv"]:
        if path.startswith("/in/"):
            assert path[len("/in/"):] in plan["files"]


def test_tool_based_inputs_carry_every_tool_of_the_scenario():
    for name in ["lethal-trifecta-lint", "mcp-trifecta", "triflow"]:
        text = " ".join(ADAPTERS[name].build_input(tools("filesystem-fetch"), CONFIGS)["files"].values())
        for tool in tools("filesystem-fetch"):
            assert f'"{tool["name"]}"' in text, (name, tool["name"])


def test_server_based_input_names_every_server_with_its_launch_command():
    config = json.loads(trifecta_check.build_input(tools("filesystem-fetch"), CONFIGS)["files"]["mcp.json"])
    assert config["mcpServers"]["fetch"] == CONFIGS["fetch"]
    assert set(config["mcpServers"]) == {"filesystem", "fetch"}


@pytest.mark.parametrize("name,scenario_id,expected", [
    ("lethal-trifecta-lint", "github-alone", True),
    ("lethal-trifecta-lint", "filesystem-fetch", False),
    ("mcp-trifecta", "slack-alone", True),
    ("mcp-trifecta", "filesystem-fetch", False),
    ("triflow", "supabase-alone", True),
    ("triflow", "filesystem-fetch", False),
    ("trifecta-check", "github-alone", False),
    ("trifecta-check", "filesystem-fetch", False),
])
def test_parsers_read_the_saved_real_outputs(name, scenario_id, expected):
    raw = (ROOT / "results" / "raw" / name / f"{scenario_id}.out").read_text()
    parsed = ADAPTERS[name].parse(raw, tools(scenario_id))
    assert parsed["verdict"] is expected
    if name != "trifecta-check":
        assert set(parsed["tool_labels"]) <= {f"{t['server']}/{t['name']}" for t in tools(scenario_id)}
        assert all(set(v) <= {"P", "U", "E"} for v in parsed["tool_labels"].values())


def test_unparseable_output_raises_so_the_runner_records_an_error():
    for adapter in ADAPTERS.values():
        with pytest.raises(Exception):
            adapter.parse("Traceback: boom", tools("fetch-alone"))
