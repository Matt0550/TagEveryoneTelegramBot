# syntax=docker/dockerfile:1

# Use the latest stable Python version
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim as base

<<<<<<< HEAD
# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
=======
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
>>>>>>> parent of ed7058e (Update)

WORKDIR /home

# Arguments for user creation
ARG APP_USER=appuser
ENV APP_USER=${APP_USER}
ARG APP_UID=1000
ARG APP_GID=1000

# Create a non-root user to run the application for better security
RUN groupadd -g ${APP_GID} ${APP_USER} && \
    useradd -u ${APP_UID} -g ${APP_GID} -M -s /usr/sbin/nologin ${APP_USER}

<<<<<<< HEAD
# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    dos2unix \
    gosu \
    curl && \
    rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size
=======
RUN apt-get update && apt-get install -y gosu dos2unix
>>>>>>> parent of ed7058e (Update)

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

<<<<<<< HEAD
# Ensure the init script is executable, process it with dos2unix, and set proper ownership
RUN dos2unix /home/scripts/init.sh && \
    chmod +x /home/scripts/init.sh && \
    chown -R ${APP_USER}:${APP_USER} /home
=======
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
>>>>>>> parent of ed7058e (Update)

# Change the user to the non-root user early
USER ${APP_USER}

# Expose the application port
EXPOSE 5000

<<<<<<< HEAD
# Set the entrypoint for the container
=======
>>>>>>> parent of ed7058e (Update)
ENTRYPOINT [ "/bin/bash", "/home/scripts/init.sh" ]
