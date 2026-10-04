"""eb4890/trifecta-check: judges server names in an mcpServers config; never reads tools."""
import json

from .common import dump, servers_in_order


def build_input(tools, configs):
    servers = {name: {"command": configs[name]["command"], "args": configs[name]["args"]} for name in servers_in_order(tools)}
    return {"files": {"mcp.json": dump({"mcpServers": servers})}, "argv": ["python", "/shim.py", "/in/mcp.json"]}


def parse(stdout, tools):
    report = json.loads(stdout[stdout.index("{"):])
    return {"verdict": bool(report["has_trifecta"]), "tool_labels": None,
            "detail": "server findings: " + ", ".join(sorted(report["capabilities"])) if report["capabilities"] else "no findings"}
