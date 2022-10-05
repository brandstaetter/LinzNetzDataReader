FROM python:3.9.6-slim AS base
ENV DEBIAN_FRONTEND=noninteractive
# ENV TZ=Etc/UTC
# ENV PIP_DEFAULT_TIMEOUT=3600

# ENV PIP_NO_CACHE_DIR=true
# RUN python -m pip install -U pip setuptools wheel

WORKDIR /app/data_analyzer

RUN apt-get update && apt-get install -y --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/*
RUN pip install pre-commit
RUN git init
COPY .pre-commit-config.yaml ./
RUN pre-commit install-hooks

COPY . .
RUN git add .
CMD ["/bin/bash", "-c", "pre-commit run --all-files"]
