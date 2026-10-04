# Lonkins/triflow at a pinned commit, with its declared dependencies installed at build time.
FROM python:3.12-slim
ADD https://github.com/Lonkins/triflow/archive/c555768cdc26416e59b00669a6a06717005289ac.tar.gz /tmp/src.tgz
RUN mkdir /checker && tar -xzf /tmp/src.tgz -C /checker --strip-components=1 && rm /tmp/src.tgz \
    && pip install --no-cache-dir /checker && useradd -m bench
COPY shim.py /shim.py
ENV PYTHONDONTWRITEBYTECODE=1
USER bench
