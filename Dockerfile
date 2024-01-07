# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.9.2
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /home

ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

RUN apt-get update && apt-get install -y gosu

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY /src /src

RUN chown -R ${APP_USER}:${APP_USER} /src

COPY /scripts /scripts
RUN chmod +x /scripts/*

# Expose the port that the application listens on.
EXPOSE 5000

VOLUME [ "/src/db/input" ]

ENTRYPOINT [ "/scripts/init.sh" ]