# ==========================================
# Stage 1: The Builder
# ==========================================
FROM python:3.13-slim-trixie AS builder
ARG DEBIAN_FRONTEND=noninteractive

# 1. Install Build Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make uv available
ENV PATH="/root/.local/bin:$PATH" \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3

# 3. Set Up Environment
WORKDIR /code
RUN /root/.local/bin/uv venv .venv

# 4. Install Python Dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev


# ==========================================
# Stage 2: The Final Runtime Image
# ==========================================
FROM python:3.13-slim-trixie AS final
ARG DEBIAN_FRONTEND=noninteractive

# 1. Set Environment Variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CODE_DIR=/code \
    VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH"

# 2. Install Runtime System Dependencies
RUN apt-get update && apt-get install -y \
    nano curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 3. Create Non-Root User
RUN useradd --create-home --shell /bin/bash --system appuser

# 4. Set Working Directory
WORKDIR /code
RUN mkdir -p /uwsgi /log

# 5. Copy Virtual Environment (From Builder)
COPY --from=builder --chown=appuser:appuser /code/.venv ./.venv

# 6. Copy your application code
COPY --chown=appuser:appuser . $CODE_DIR

# 7. Give the appuser ownership of the app directory (Combined cleanup)
RUN chown -R appuser:appuser $CODE_DIR

# 8. Switch to the non-root user
USER appuser

# 9. Expose port
EXPOSE 8080

# 10. Execute Gunicorn directly as PID 1
CMD ["/code/.venv/bin/python3", \
     "-m", "gunicorn", "DjangoCustomLog.asgi:application", \
     "-c", "/code/DjangoCustomLog/gunicorn.py"]
