# Use official Playwright image as base
# FROM mcr.microsoft.com/playwright:v1.44.0-jammy
FROM mcr.microsoft.com/playwright:v1.30.0-focal


# Install Python 3.12 and other build tools
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3.12-dev \
    curl build-essential \
    && ln -sf /usr/bin/python3.12 /usr/local/bin/python3 \
    && ln -sf /usr/bin/python3.12 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3.12 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /code

# Copy project files (update as needed)
COPY pyproject.toml poetry.lock* /code/

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

ENV PATH="/root/.local/bin:$PATH"

# Copy rest of the app
COPY . /code/

EXPOSE 8080

ENTRYPOINT ["poetry", "run", "uvicorn", "fastapi_server.main:app", "--app-dir", "src/main", "--host", "0.0.0.0", "--port", "8080"]
# ENTRYPOINT ["sh", "-c", "sleep 2703600"]
