# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home

ARG APP_USER=appuser
ARG APP_UID=1000
ARG APP_GID=1000
ENV APP_USER=${APP_USER}

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    gosu && \
    rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

RUN dos2unix /home/scripts/init.sh && \
    chmod +x /home/scripts/init.sh && \
    chown -R ${APP_USER}:${APP_USER} /home

VOLUME [ "/home/src/db/input" ]

EXPOSE 5000

ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]