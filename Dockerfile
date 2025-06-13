FROM mcr.microsoft.com/playwright:v1.30.0-focal

# Set the working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
   
# Copy the rest of the application
COPY . .
EXPOSE 8080

ENTRYPOINT ["poetry", "run", "uvicorn", "main.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8080"]