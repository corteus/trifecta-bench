# Listing image: every MCP server pinned, run with --network none, only tools/list is asked.
FROM ghcr.io/github/github-mcp-server@sha256:7aaeeec9ae4fe9a736d100c1ff0798f3c219b5009e05f5d3945fcacb13cc196b AS github

FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g --ignore-scripts=false \
      @supabase/mcp-server-supabase@0.13.0 \
      @playwright/mcp@0.0.83 \
      @notionhq/notion-mcp-server@2.5.2 \
      slack-mcp-server@1.3.0 \
      @modelcontextprotocol/server-filesystem@2026.8.31 \
      @modelcontextprotocol/server-memory@2026.8.31
RUN python3 -m venv /opt/py && /opt/py/bin/pip install --no-cache-dir mcp-server-fetch==2026.8.18 mcp-server-git==2026.8.18
COPY --from=github /server/github-mcp-server /server/github-mcp-server
RUN mkdir -p /data/repo && git -C /data/repo init -q && useradd -m lister && chown -R lister /data
COPY list_tools.py /list_tools.py
USER lister
ENTRYPOINT ["python3", "/list_tools.py"]
