# syntax=docker/dockerfile:1

# Use the latest stable Python version
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /home

# Arguments for user creation
ARG APP_USER=appuser
ARG APP_UID=1000
ARG APP_GID=1000
ENV APP_USER=${APP_USER}

# Create a non-root user to run the application for better security
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    gosu \
    curl && \
    rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size

# Stage for installing Python dependencies (using pip with cache optimization)
FROM base as build

# Install required Python dependencies using pip with cache optimization
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --no-cache-dir -r requirements.txt

# Use a multi-stage build to reduce the final image size
FROM base

# Copy Python dependencies from the build stage to the final image
COPY --from=build /usr/local /usr/local

# Copy the rest of the application files
COPY . .

# Ensure the init script is executable, process it with dos2unix, and set proper ownership
RUN dos2unix /home/scripts/init.sh && \
    chmod +x /home/scripts/init.sh && \
    chown -R ${APP_USER}:${APP_USER} /home

# Change the user to the non-root user early
USER ${APP_USER}

# Expose the application port
EXPOSE 5000

# Set the entrypoint for the container
ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]
