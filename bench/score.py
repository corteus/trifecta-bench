"""Scoring for trifecta-bench: our labels decide the expected verdict, checkers are compared to it.

P = private data, U = untrusted content, E = external communication.
A scenario has the lethal trifecta when its tools together cover P, U and E.
"""

LABELS = ("P", "U", "E")


def capabilities(tools):
    """The set of capabilities a list of tools grants."""
    found = set()
    for tool in tools:
        for label in tool["labels"]:
            if label not in LABELS:
                raise ValueError(f"unknown label {label!r} on tool {tool['name']!r}")
            found.add(label)
    return found


def scenario_tools(scenario, servers):
    """Every tool of every server in the scenario, tagged with its server."""
    tools = []
    for name in scenario["servers"]:
        for tool in servers[name]["tools"]:
            tools.append({**tool, "server": name})
    return tools


def expected_verdict(scenario, servers):
    return capabilities(scenario_tools(scenario, servers)) == set(LABELS)


def _tool_index(servers):
    return {f"{name}/{tool['name']}": set(tool["labels"]) for name, server in servers.items() for tool in server["tools"]}


def score(results, scenarios, servers):
    """Per checker: hits, misses, false alarms, errors, the GitHub case and label agreement."""
    by_id = {s["id"]: s for s in scenarios}
    labels = _tool_index(servers)
    scores = {}
    for r in results:
        if r["scenario"] not in by_id:
            raise KeyError(f"unknown scenario {r['scenario']!r}")
        s = scores.setdefault(r["checker"], {
            "tp": 0, "fn": 0, "fp": 0, "tn": 0, "errors": 0, "github_single_server": "not run",
            "labels_compared": 0, "labels_matched": 0, "labels_unknown_tools": 0,
        })
        ran = r["status"] == "ok" and r["verdict"] is not None
        if r["scenario"] == "github-alone":
            s["github_single_server"] = ("flagged" if r["verdict"] else "missed") if ran else "error"
        if not ran:
            s["errors"] += 1
            continue
        expected = expected_verdict(by_id[r["scenario"]], servers)
        key = {(True, True): "tp", (True, False): "fn", (False, True): "fp", (False, False): "tn"}[(expected, bool(r["verdict"]))]
        s[key] += 1
        for tool_key, tool_labels in (r.get("tool_labels") or {}).items():
            if tool_key not in labels:
                s["labels_unknown_tools"] += 1
                continue
            s["labels_compared"] += 1
            if set(tool_labels) == labels[tool_key]:
                s["labels_matched"] += 1
    return scores


def render_table(scores):
    """A Markdown table, one row per checker, sorted by name."""
    rows = [
        "| Checker | Trifectas caught | Missed | False alarms | Correct all-clear | Errors | GitHub alone | Tool labels matching ours |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in sorted(scores):
        s = scores[name]
        positives = s["tp"] + s["fn"]
        agreement = f"{s['labels_matched']}/{s['labels_compared']}" if s["labels_compared"] else "n/a"
        rows.append(
            f"| {name} | {s['tp']}/{positives} | {s['fn']} | {s['fp']} | {s['tn']} | {s['errors']} | {s['github_single_server']} | {agreement} |"
        )
    return "\n".join(rows)
