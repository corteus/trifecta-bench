# eb4890/trifecta-check at a pinned commit. Stale bytecode shipped in the repo is removed before use.
FROM python:3.12-slim
ADD https://github.com/eb4890/trifecta-check/archive/adc104a0b8c9c76bab766a023098626a478e353a.tar.gz /tmp/src.tgz
RUN mkdir /checker && tar -xzf /tmp/src.tgz -C /checker --strip-components=1 && rm /tmp/src.tgz \
    && find /checker -name '__pycache__' -type d -prune -exec rm -r {} + \
    && pip install --no-cache-dir /checker && useradd -m bench
COPY shim.py /shim.py
ENV PYTHONDONTWRITEBYTECODE=1
USER bench
