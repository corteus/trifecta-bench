"""tusharislampure29/mcp-trifecta: native fleet manifest, union verdict across servers."""
import json

from .common import dump, servers_in_order

CAPS = {"private_data": "P", "untrusted_content": "U", "exfil": "E"}


def build_input(tools, configs):
    servers = []
    for name in servers_in_order(tools):
        cfg = configs[name]
        servers.append({"name": name, "command": cfg["command"], "args": cfg["args"], "env": {},
                        "tools": [{"name": t["name"], "description": t.get("description", "")} for t in tools if t["server"] == name]})
    return {"files": {"fleet.json": dump({"name": "scenario", "servers": servers})},
            "argv": ["python", "-m", "trifecta", "scan", "/in/fleet.json", "-f", "json", "--fail-on", "never"]}


def parse(stdout, tools):
    report = json.loads(stdout[stdout.index("{"):])
    known = {f"{t['server']}/{t['name']}" for t in tools}
    labels = {key: [] for key in known}
    for cap, entries in report["capability_map"].items():
        if cap not in CAPS:
            continue
        for entry in entries:
            server, _, name = entry.partition("::")
            key = f"{server}/{name}"
            if key in labels:
                labels[key].append(CAPS[cap])
    labels = {k: sorted(set(v), key="PUE".index) for k, v in labels.items()}
    return {"verdict": bool(report["trifecta_present"]), "tool_labels": labels,
            "detail": f"cross_server={report.get('cross_server')} risk={report.get('risk_score')}"}
