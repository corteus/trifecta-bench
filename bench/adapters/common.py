"""Shared helpers for adapters. An adapter turns one scenario into a checker's input
and the checker's output into {verdict, tool_labels, detail}."""
import json

CAP = {"P", "U", "E"}


def tool_entry(tool):
    """The fields a real tools/list answer gives, nothing of our labels."""
    entry = {"name": tool["name"], "description": tool.get("description", "")}
    if tool.get("inputSchema") is not None:
        entry["inputSchema"] = tool["inputSchema"]
    return entry


def servers_in_order(tools):
    seen = []
    for t in tools:
        if t["server"] not in seen:
            seen.append(t["server"])
    return seen


def name_index(tools):
    """tool name -> "server/name"; names are unique inside every scenario we use."""
    index = {}
    for t in tools:
        if t["name"] in index:
            raise ValueError(f"tool name {t['name']} appears in two servers of one scenario")
        index[t["name"]] = f"{t['server']}/{t['name']}"
    return index


def dump(obj):
    return json.dumps(obj, indent=2, sort_keys=True)
