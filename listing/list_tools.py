"""Ask one MCP server for its tools over stdio and print them as JSON.

Runs inside the listing container with no network. Only initialize and
tools/list are sent, and no tool is ever called.
"""
import json
import os
import subprocess
import sys
import threading

SERVERS = {
    "github": {"command": ["/server/github-mcp-server", "stdio"], "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "placeholder"}},
    "supabase": {"command": ["mcp-server-supabase", "--access-token", "placeholder"], "env": {}},
    # The docs feature fetches a schema from Supabase while listing, which fails without network.
    # The other seven features are listed here and the docs tool is taken from source.
    "supabase-nodocs": {"command": ["mcp-server-supabase", "--access-token", "placeholder", "--features", "account,database,debugging,development,functions,branching,storage"], "env": {}},
    "playwright": {"command": ["playwright-mcp"], "env": {}},
    "notion": {"command": ["notion-mcp-server"], "env": {"NOTION_TOKEN": "placeholder"}},
    "slack": {"command": ["slack-mcp-server", "--transport", "stdio"], "env": {"SLACK_MCP_XOXP_TOKEN": "xoxp-placeholder"}},
    "filesystem": {"command": ["mcp-server-filesystem", "/data"], "env": {}},
    "memory": {"command": ["mcp-server-memory"], "env": {}},
    "fetch": {"command": ["/opt/py/bin/mcp-server-fetch"], "env": {}},
    "git": {"command": ["/opt/py/bin/mcp-server-git", "--repository", "/data/repo"], "env": {}},
}

TIMEOUT = 60


def main(name):
    spec = SERVERS[name]
    env = {**os.environ, **spec["env"]}
    proc = subprocess.Popen(spec["command"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True, bufsize=1)
    stderr_lines = []
    threading.Thread(target=lambda: stderr_lines.extend(proc.stderr), daemon=True).start()
    timer = threading.Timer(TIMEOUT, proc.kill)
    timer.start()

    def send(message):
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def wait_for(request_id):
        for line in proc.stdout:
            line = line.strip()
            if not line.startswith("{"):
                continue
            message = json.loads(line)
            if message.get("id") == request_id:
                return message
        raise RuntimeError("server closed before answering: " + "".join(stderr_lines)[-1500:])

    try:
        send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "trifecta-bench", "version": "0.1.0"}}})
        init = wait_for(1)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, cursor, request_id = [], None, 2
        while True:
            send({"jsonrpc": "2.0", "id": request_id, "method": "tools/list", "params": {"cursor": cursor} if cursor else {}})
            page = wait_for(request_id)
            if "error" in page:
                raise RuntimeError(f"tools/list error: {page['error']}")
            tools += page["result"]["tools"]
            cursor = page["result"].get("nextCursor")
            request_id += 1
            if not cursor:
                break
        server_info = init.get("result", {}).get("serverInfo", {})
        print(json.dumps({"server": name, "serverInfo": server_info, "tools": tools}, indent=2, sort_keys=True))
    finally:
        timer.cancel()
        proc.kill()


if __name__ == "__main__":
    main(sys.argv[1])
