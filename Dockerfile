FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-dashboard.txt .
RUN pip install -r requirements-dashboard.txt

COPY dashboard/ dashboard/

EXPOSE 8050

# El dataset se monta en /app/data (ver docker-compose.yml); la caché parquet se genera al iniciar.
CMD ["gunicorn", "dashboard.app:server", "--bind", "0.0.0.0:8050", "--workers", "1", "--timeout", "300"]
