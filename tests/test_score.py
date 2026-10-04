"""Scorer tests (SPEC-CORTEUS-TRIFECTA-BENCH-001). Pure, no Docker."""

import pytest

from bench.score import (
    capabilities,
    expected_verdict,
    render_table,
    scenario_tools,
    score,
)


def tool(name, labels):
    return {"name": name, "description": f"{name} tool", "labels": labels, "reasons": {l: "test" for l in labels}}


SERVERS = {
    "github": {"server": "github", "tools": [tool("get_issue", ["U"]), tool("get_file_contents", ["P", "U"]), tool("create_pull_request", ["E"])]},
    "filesystem": {"server": "filesystem", "tools": [tool("read_file", ["P"]), tool("write_file", [])]},
    "fetch": {"server": "fetch", "tools": [tool("fetch", ["U", "E"])]},
    "memory": {"server": "memory", "tools": [tool("read_graph", ["P"])]},
}

SCENARIOS = [
    {"id": "github-alone", "servers": ["github"]},
    {"id": "filesystem-fetch", "servers": ["filesystem", "fetch"]},
    {"id": "filesystem-alone", "servers": ["filesystem"]},
    {"id": "memory-alone", "servers": ["memory"]},
]


def test_capabilities_is_the_union_of_tool_labels():
    assert capabilities(SERVERS["github"]["tools"]) == {"P", "U", "E"}
    assert capabilities(SERVERS["filesystem"]["tools"]) == {"P"}
    assert capabilities([]) == set()


def test_unknown_label_is_rejected():
    with pytest.raises(ValueError):
        capabilities([tool("x", ["Q"])])


def test_expected_verdict_follows_the_labels():
    assert expected_verdict(SCENARIOS[0], SERVERS) is True
    assert expected_verdict(SCENARIOS[1], SERVERS) is True
    assert expected_verdict(SCENARIOS[2], SERVERS) is False
    with pytest.raises(KeyError):
        expected_verdict({"id": "x", "servers": ["nope"]}, SERVERS)


def test_scenario_tools_keep_their_server():
    tools = scenario_tools(SCENARIOS[1], SERVERS)
    assert [(t["server"], t["name"]) for t in tools] == [("filesystem", "read_file"), ("filesystem", "write_file"), ("fetch", "fetch")]


def result(checker, scenario, verdict, status="ok", tool_labels=None):
    return {"checker": checker, "scenario": scenario, "status": status, "verdict": verdict, "tool_labels": tool_labels, "detail": ""}


def test_score_counts_hits_misses_false_alarms_and_errors():
    results = [
        result("a", "github-alone", True),
        result("a", "filesystem-fetch", True),
        result("a", "filesystem-alone", False),
        result("a", "memory-alone", True),
        result("b", "github-alone", False),
        result("b", "filesystem-fetch", None, status="error"),
        result("b", "filesystem-alone", False),
        result("b", "memory-alone", False),
    ]
    scores = score(results, SCENARIOS, SERVERS)
    a, b = scores["a"], scores["b"]
    assert (a["tp"], a["fn"], a["fp"], a["tn"], a["errors"]) == (2, 0, 1, 1, 0)
    assert (b["tp"], b["fn"], b["fp"], b["tn"], b["errors"]) == (0, 1, 0, 2, 1)
    assert a["github_single_server"] == "flagged"
    assert b["github_single_server"] == "missed"


def test_github_case_reports_error_and_not_run():
    scores = score([result("c", "github-alone", None, status="unsupported")], SCENARIOS, SERVERS)
    assert scores["c"]["github_single_server"] == "error"
    assert scores["c"]["errors"] == 1
    assert score([result("d", "filesystem-alone", False)], SCENARIOS, SERVERS)["d"]["github_single_server"] == "not run"


def test_label_agreement_compares_only_tools_the_checker_labelled():
    labels = {"github/get_issue": ["U"], "github/get_file_contents": ["P"], "github/unknown_tool": ["E"]}
    scores = score([result("a", "github-alone", True, tool_labels=labels)], SCENARIOS, SERVERS)
    assert scores["a"]["labels_compared"] == 2
    assert scores["a"]["labels_matched"] == 1
    assert scores["a"]["labels_unknown_tools"] == 1


def test_results_for_unknown_scenarios_are_rejected():
    with pytest.raises(KeyError):
        score([result("a", "nope", True)], SCENARIOS, SERVERS)


def test_render_table_is_stable_and_names_every_checker():
    results = [result("b", "github-alone", False), result("a", "github-alone", True)]
    table = render_table(score(results, SCENARIOS, SERVERS))
    lines = table.splitlines()
    assert lines[0].startswith("| Checker |")
    assert lines[2].startswith("| a |") and lines[3].startswith("| b |")
    assert render_table(score(results, SCENARIOS, SERVERS)) == table
