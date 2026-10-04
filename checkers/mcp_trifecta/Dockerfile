# tusharislampure29/mcp-trifecta at a pinned commit. It uses the standard library only.
FROM python:3.12-slim
ADD https://github.com/tusharislampure29/mcp-trifecta/archive/83513635fc842f3899489afeb6194aaead6f6ffb.tar.gz /tmp/src.tgz
RUN mkdir /checker && tar -xzf /tmp/src.tgz -C /checker --strip-components=1 && rm /tmp/src.tgz && useradd -m bench
ENV PYTHONPATH=/checker PYTHONDONTWRITEBYTECODE=1
WORKDIR /checker
USER bench
