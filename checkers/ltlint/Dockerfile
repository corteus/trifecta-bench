# fevziegeyurtsevenler/lethal-trifecta-lint at a pinned commit. It has no dependencies.
FROM python:3.12-slim
ADD https://github.com/fevziegeyurtsevenler/lethal-trifecta-lint/archive/33a4d570fae809f33c2f92ba9f80311e7ec56e07.tar.gz /tmp/src.tgz
RUN mkdir /checker && tar -xzf /tmp/src.tgz -C /checker --strip-components=1 && rm /tmp/src.tgz && useradd -m bench
ENV PYTHONPATH=/checker PYTHONDONTWRITEBYTECODE=1
WORKDIR /checker
USER bench
