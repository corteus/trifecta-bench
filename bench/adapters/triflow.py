"""Lonkins/triflow: tool lists only through its Python API (see checkers/triflow/shim.py)."""
import json

from .common import dump, servers_in_order, tool_entry

CAPS = {"private_data_source": "P", "untrusted_content_ingress": "U", "exfiltration_channel": "E"}


def build_input(tools, configs):
    servers = [{"name": name, "command": configs[name]["command"], "args": configs[name]["args"],
                "tools": [tool_entry(t) for t in tools if t["server"] == name]} for name in servers_in_order(tools)]
    return {"files": {"scenario.json": dump({"servers": servers})}, "argv": ["python", "/shim.py", "/in/scenario.json"]}


def parse(stdout, tools):
    report = json.loads(stdout[stdout.index("{"):])
    known = {f"{t['server']}/{t['name']}" for t in tools}
    labels = {}
    for server in report["servers"]:
        name = server["slug"].split(":", 1)[-1]
        for tool in server["tools"]:
            key = f"{name}/{tool['name']}"
            if key in known:
                labels[key] = sorted({CAPS[c] for c in tool["capabilities"] if c in CAPS}, key="PUE".index)
    trifecta = [f for f in report["findings"] if f["rule_id"] == "TRIFLOW-TRIFECTA"]
    return {"verdict": bool(trifecta), "tool_labels": labels,
            "detail": "; ".join(f["title"] for f in trifecta) or "no trifecta finding"}
