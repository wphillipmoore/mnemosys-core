FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
COPY LICENSE /app/LICENSE
COPY src /app/src
RUN pip install --no-cache-dir --no-deps /app
COPY scripts/runtime/entrypoint.sh /app/scripts/runtime/entrypoint.sh

RUN chmod +x /app/scripts/runtime/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/scripts/runtime/entrypoint.sh"]
