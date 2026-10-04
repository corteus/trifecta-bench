"""Run every checker on every scenario in Docker and score the results.

Each run: one fresh container, no network, read-only filesystem, the scenario
input mounted read-only at /in, nothing else from the host.
"""
import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from bench.score import render_table, scenario_tools, score

ROOT = Path(__file__).resolve().parent.parent
CHECKERS = {
    "lethal-trifecta-lint": ("ltlint", "trifecta-bench-ltlint:0.1"),
    "mcp-trifecta": ("mcp_trifecta", "trifecta-bench-mcp_trifecta:0.1"),
    "triflow": ("triflow", "trifecta-bench-triflow:0.1"),
    "trifecta-check": ("trifecta_check", "trifecta-bench-trifecta_check:0.1"),
}
NOT_APPLICABLE = {
    "tracewall": "a runtime firewall that judges individual tool calls during a session, with no input for a tool list",
}


def load():
    servers = {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / "data" / "servers").glob("*.json"))}
    scenarios = json.loads((ROOT / "data" / "scenarios.json").read_text())
    configs = json.loads((ROOT / "data" / "server_configs.json").read_text())
    return servers, scenarios, configs


def run_one(adapter, image, tools, configs):
    plan = adapter.build_input(tools, configs)
    with tempfile.TemporaryDirectory() as tmp:
        for name, text in plan["files"].items():
            (Path(tmp) / name).write_text(text)
        cmd = ["docker", "run", "--rm", "--network", "none", "--read-only", "--tmpfs", "/tmp",
               "--security-opt", "no-new-privileges", "-v", f"{tmp}:/in:ro", image, *plan["argv"]]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    raw_out = proc.stdout
    try:
        parsed = adapter.parse(proc.stdout, tools)
        return {"status": "ok", **parsed, "exit_code": proc.returncode, "_raw": raw_out}
    except Exception as error:  # a checker that cannot run is a result, not a crash
        return {"status": "error", "verdict": None, "tool_labels": None, "exit_code": proc.returncode, "_raw": raw_out,
                "detail": f"{type(error).__name__}: {error}; stderr: {proc.stderr[-400:]}"}


def main():
    servers, scenarios, configs = load()
    results = []
    for checker, (module, image) in CHECKERS.items():
        adapter = importlib.import_module(f"bench.adapters.{module}")
        for scenario in scenarios:
            outcome = run_one(adapter, image, scenario_tools(scenario, servers), configs)
            raw_dir = ROOT / "results" / "raw" / checker
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / f"{scenario['id']}.out").write_text(outcome.pop("_raw"))
            results.append({"checker": checker, "scenario": scenario["id"], **outcome})
            print(f"{checker:<22} {scenario['id']:<20} {outcome['status']:<6} verdict={outcome['verdict']}", file=sys.stderr)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps({"results": results, "not_applicable": NOT_APPLICABLE}, indent=2, sort_keys=True) + "\n")
    table = render_table(score(results, scenarios, servers))
    na = "\n".join(f"| {name} | not applicable: {why} |" for name, why in NOT_APPLICABLE.items())
    (out / "table.md").write_text(table + "\n\n| Checker | Note |\n| --- | --- |\n" + na + "\n")
    print(table)


if __name__ == "__main__":
    main()
