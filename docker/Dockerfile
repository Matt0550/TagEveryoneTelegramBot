# syntax=docker/dockerfile:1

FROM python:3.14

# Labels
LABEL org.opencontainers.image.title="TagEveryoneTelegramBot"
LABEL org.opencontainers.image.description="Telegram bot for tagging group members"
LABEL org.opencontainers.image.authors="Matt0550"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode for faster startup
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install dependencies first (most cacheable layer)
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy project files
COPY ./pyproject.toml ./uv.lock /app/
COPY ./alembic.ini /app/

# Copy application source code
COPY ./src /app/src

# Sync the project (install the project itself)
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Create necessary directories with correct permissions
RUN mkdir -p /app/src/db/input \
    && mkdir -p /app/src/logs \
    && chown -R appuser:appuser /app

# Database volume — SQLite DB stored here
VOLUME ["/app/src/db/input"]

# Switch to non-root user
USER appuser

# Default working directory for all services (src is the Python root)
WORKDIR /app/src

# Default CMD — bot (override in docker-compose for api/celery)
CMD ["python", "bot/main.py"]