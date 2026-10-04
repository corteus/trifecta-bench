# trifecta-bench

We wanted to know whether the small open-source "lethal trifecta" checkers catch real problems. So we ran four of them on the tools of nine MCP servers that people actually install, and kept every input and output here.

The lethal trifecta is [Simon Willison's name](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) for an agent that can read private data, takes in text someone else wrote, and has a way to send data out. With all three, one prompt injection in that outside text can walk off with the private data.

## What we found, 4 October 2026

| Checker | Trifectas caught | With the right reason for all three | False alarms | GitHub server alone |
| --- | --- | --- | --- | --- |
| [mcp-trifecta](https://github.com/tusharislampure29/mcp-trifecta) | 5 of 7 | 2 | 0 | caught |
| [triflow](https://github.com/Lonkins/triflow) | 3 of 7 | 1 | 0 | caught |
| [lethal-trifecta-lint](https://github.com/fevziegeyurtsevenler/lethal-trifecta-lint) | 2 of 7 | 1 | 0 | caught |
| [trifecta-check](https://github.com/eb4890/trifecta-check) | 0 of 7 | not applicable | 0 | missed |

A catch counts as "right reason" only when the checker pointed at a real private-data tool, a real untrusted-content tool and a real way out.

All four missed local files plus `fetch`. Each one that reads tools labels `fetch` as untrusted input, and none of them as a way out, although loading a URL is enough to carry data to an attacker.

mcp-trifecta caught the most, but three of its five catches rest on the wrong tools. It flagged git plus fetch because it took the local `git_commit` and `git_log` for exfiltration.

GitHub's server on its own was caught by three of the four. trifecta-check missed it because it reads server names and never looks at tools.

None of the checkers reads the `readOnlyHint` or `openWorldHint` annotations that seven of the eight servers we listed live publish. The fetch server publishes none, so annotations would not have rescued that case either.

No checker raised a false alarm. Our six safe scenarios are simple, though, so that says little about noise on a real setup.

Per scenario detail is in [results/table.md](results/table.md) and [results/analysis.md](results/analysis.md). The raw output of every run is in `results/raw/`.

## How we labelled the tools

Every one of the 180 tools carries the capabilities it grants and one line of reasoning, in `data/servers/*.json`.

- **P, private data.** Returns data the user can see and outsiders cannot: private repositories, databases, local files, workspace pages, DMs.
- **U, untrusted content.** Returns text that someone other than the user can write: public issues, web pages, other people's messages.
- **E, external communication.** Writes free text where someone other than the user can read it, or sends a request to an outside address.

A scenario has the trifecta when its tools together cover all three. These are our calls, and two of them are close. Slack's default setup has no message tool, so it reaches E only through user group descriptions that every workspace member can read. Notion writes count as E because teammates and guests read the workspace. If you disagree, the reason sits next to the label.

## Servers

| Server | Version | How we got the tool list |
| --- | --- | --- |
| github/github-mcp-server | v1.14.0, image digest in `listing/Dockerfile` | `tools/list`, default toolsets |
| @supabase/mcp-server-supabase | 0.13.0 | `tools/list` for seven features, `search_docs` from the package source, because the docs feature fetches a schema while listing |
| @playwright/mcp | 0.0.83 | `tools/list` |
| @notionhq/notion-mcp-server | 2.5.2 | `tools/list` |
| korotovsky/slack-mcp-server | v1.3.0 | from source, because it contacts Slack at startup. Default setup: a user token and no optional tools, 17 of 22 |
| @modelcontextprotocol/server-filesystem, server-memory | 2026.8.31 | `tools/list` |
| mcp-server-fetch, mcp-server-git | 2026.8.18 | `tools/list` |

Listing ran in a container with no network, and only `initialize` and `tools/list` were sent. Tool names and descriptions are quoted from each project under its own licence.

The thirteen scenarios in `data/scenarios.json` are five single servers that hold all three capabilities by our labels, four that do not, two pairs that form the trifecta only together (filesystem with fetch, git with fetch) and two pairs that never do.

## Checkers

| Checker | Commit | How we ran it |
| --- | --- | --- |
| lethal-trifecta-lint | 33a4d57 | its CLI on a tool list |
| mcp-trifecta | 8351363 | its CLI `scan` on its own fleet manifest |
| triflow | c555768 | its Python API, the route its own tests use, because the CLI would launch the servers |
| trifecta-check | adc104a | the three scanners its CLI runs, on an `mcpServers` config |
| [tracewall](https://github.com/VinayJogani14/tracewall) | f472e38 | not run. It is a runtime firewall that judges tool calls during a session and has no input for a tool list |

We ran each checker unmodified, in a fresh Docker container per run, with no network, a read-only filesystem and the scenario mounted read-only. Two full runs gave identical results.

## Limits

The labels are judgement. Thirteen scenarios is a small set. The checkers are young and will change, which is why each one is pinned to a commit. A static check also cannot see what a configured token is allowed to do.

## Run it

```sh
uv venv .venv && uv pip install --python .venv/bin/python pytest
.venv/bin/python -m pytest
docker build -t trifecta-bench-listing:0.1 listing        # only to list the tools again
for c in ltlint mcp_trifecta triflow trifecta_check; do docker build -t trifecta-bench-$c:0.1 checkers/$c; done
.venv/bin/python -m bench.run && .venv/bin/python -m bench.analysis
```

To add a checker, write a Dockerfile under `checkers/`, an adapter in `bench/adapters/` with `build_input` and `parse`, an entry in `bench/run.py`, and a test on its saved output.

## Licence

The code is MIT. Our labels, scenarios and results are CC BY 4.0. Made by [Corteus](https://corteus.com).
