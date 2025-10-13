FROM --platform=arm64 python:3.12-slim 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for building Python packages and PostgreSQL client libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install, but exclude 'ollama' per project constraint
COPY ../requirements.txt  requirements.txt
RUN grep -v -i '^\s*ollama' requirements.txt | sed '/^\s*$/d' > requirements_no_ollama.txt \
    && pip install --no-cache-dir -r requirements_no_ollama.txt

# Copy the project
COPY .. /app

# Create a non-root user and switch to it
RUN useradd -m appuser || true
USER appuser

EXPOSE 8000