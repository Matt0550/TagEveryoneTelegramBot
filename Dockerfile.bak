# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.2
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /home

ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ARG APP_UID=1000
ARG APP_GID=1000

RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

RUN apt-get update && apt-get install -y gosu dos2unix

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY . .

# Converti init.sh in stile Unix
RUN dos2unix /home/scripts/init.sh

# Debug: Verifica la struttura delle directory nel container
RUN ls -R /home

# Modifica i permessi del file direttamente
RUN chmod +x /home/scripts/init.sh

# Debug: Verifica i permessi del file init.sh
RUN ls -l /home/scripts/init.sh

# Cambia i permessi di tutta la directory di lavoro
RUN chown -R ${APP_USER}:${APP_USER} /home

VOLUME [ "/home/src/db/input" ]

EXPOSE 5000

ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]
