# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /home

# Install system dependencies in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gosu \
    dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create user early to cache this layer
ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

# Install Python dependencies first (most cacheable layer)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install -r requirements.txt

# Copy and prepare scripts
COPY scripts/ ./scripts/
RUN dos2unix /home/scripts/init.sh && \
    chmod +x /home/scripts/init.sh

# Copy application code last (changes most frequently)
COPY . .

# Set ownership in final step
RUN chown -R ${APP_USER}:${APP_USER} /home

VOLUME [ "/home/src/db/input" ]

EXPOSE 5000

ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]