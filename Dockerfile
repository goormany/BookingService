FROM python:3.12-alpine AS builder

WORKDIR /app

# poetry install
RUN apk add --no-cache gcc musl-dev libffi-dev && \
    pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./

# install dep
RUN poetry install --no-root --no-interaction --no-ansi && \
    rm -rf $POETRY_CACHE_DIR


FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache libffi

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY alembic.ini ./
COPY pytest.ini ./
COPY src/ src/

RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete 2>/dev/null || true

RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app
USER appuser


EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python src/main.py"]