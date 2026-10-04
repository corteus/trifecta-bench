"""Second look at results/results.json: were trifectas caught for the right reasons,
and how well does each checker recognise each capability on the 180 unique tools?"""
import json
from pathlib import Path

from bench.score import expected_verdict

ROOT = Path(__file__).resolve().parent.parent


def main():
    servers = {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / "data" / "servers").glob("*.json"))}
    scenarios = {s["id"]: s for s in json.loads((ROOT / "data" / "scenarios.json").read_text())}
    results = json.loads((ROOT / "results" / "results.json").read_text())["results"]
    ours = {f"{name}/{t['name']}": set(t["labels"]) for name, s in servers.items() for t in s["tools"]}
    lines = ["## Caught for the right reasons", "",
             "A catch counts here only if, for each of P, U and E, at least one tool the checker labelled with it also has it in our labels.", "",
             "| Checker | Trifectas caught | With the right reason for all three | Caught with partly wrong reasons |", "| --- | --- | --- | --- |"]
    labelled = sorted({r["checker"] for r in results if r["tool_labels"]})
    for checker in labelled:
        right, partly = [], []
        for r in results:
            if r["checker"] != checker or not r["verdict"] or not expected_verdict(scenarios[r["scenario"]], servers):
                continue
            ok = all(any(cap in v and cap in ours[k] for k, v in r["tool_labels"].items()) for cap in "PUE")
            (right if ok else partly).append(r["scenario"])
        lines.append(f"| {checker} | {len(right) + len(partly)} | {len(right)}: {', '.join(right) or 'none'} | {', '.join(partly) or 'none'} |")
    lines += ["", f"## Capability recognition on {len(ours)} unique tools", "",
              "Found = tools with the capability in our labels that the checker also gave it. Extra = tools the checker gave it that we did not.", "",
              "| Checker | P found | P extra | U found | U extra | E found | E extra |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for checker in labelled:
        theirs = {}
        for r in results:
            if r["checker"] == checker:
                theirs.update({k: set(v) for k, v in r["tool_labels"].items()})
        cells = []
        for cap in "PUE":
            truth = {k for k, v in ours.items() if cap in v}
            pred = {k for k, v in theirs.items() if cap in v}
            cells += [f"{len(truth & pred)}/{len(truth)}", str(len(pred.difference(truth)))]
        lines.append(f"| {checker} | " + " | ".join(cells) + " |")
    (ROOT / "results" / "analysis.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
