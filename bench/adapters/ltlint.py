"""fevziegeyurtsevenler/lethal-trifecta-lint: reads a tool list, union verdict."""
import json

from .common import dump, name_index, tool_entry

CAPS = {"private_data": "P", "untrusted": "U", "external_comm": "E"}


def build_input(tools, configs):
    return {"files": {"tools.json": dump({"tools": [tool_entry(t) for t in tools]})},
            "argv": ["python", "-m", "ltlint.cli", "/in/tools.json", "--json", "/dev/stdout", "--quiet", "--no-color"]}


def parse(stdout, tools):
    report = json.loads(stdout[stdout.index("{"):])
    index = name_index(tools)
    labels = {index[t["name"]]: sorted({CAPS[c] for c in t["capabilities"]}, key="PUE".index)
              for t in report["tools"] if t["name"] in index}
    return {"verdict": bool(report["trifecta"]), "tool_labels": labels,
            "detail": f"verdict={report['verdict']} present={report.get('present_capabilities')}"}
