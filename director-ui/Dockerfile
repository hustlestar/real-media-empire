FROM python:3.11-slim

# Install system dependencies including curl for uv installation
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Copy source directory needed for package installation
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY locales/ locales/

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Set PYTHONPATH for imports
ENV PYTHONPATH=/app/src

# Run the bot using uv
CMD ["uv", "run", "python", "-m", "main"]