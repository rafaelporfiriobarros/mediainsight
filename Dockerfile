
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN uv sync --locked --no-cache

ENV PATH="/app/.venv/bin:$PATH"

COPY sql/ ./sql/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

CMD ["pytest", "-q"]
