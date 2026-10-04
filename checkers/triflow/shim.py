"""Run triflow on a tool list through its Python API, the route its own tests use.
The CLI can only read client configs and would launch the servers to list tools."""
import json
import sys
from pathlib import Path

from triflow.classify import classify_fleet
from triflow.engine import analyze
from triflow.models import IntrospectedServer, ServerConfig, ToolInfo, Transport
from triflow.report.json_report import to_json

scenario = json.loads(Path(sys.argv[1]).read_text())
servers = []
for s in scenario["servers"]:
    config = ServerConfig(name=s["name"], client="trifecta-bench", config_path=Path("mcp.json"), transport=Transport.STDIO,
                          command=s["command"], args=tuple(s["args"]))
    tools = tuple(ToolInfo(name=t["name"], description=t.get("description", ""), input_schema=t.get("inputSchema") or {}) for t in s["tools"])
    servers.append(IntrospectedServer(config=config, tools=tools))
classified = classify_fleet(servers)
print(to_json(analyze(classified), servers=classified))
