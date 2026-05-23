FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
COPY ais_os ./ais_os
COPY configs ./configs

RUN pip install --no-cache-dir -r requirements.txt && pip install -e .

COPY . .

ENV AIS_WORKSPACE=/app
ENV AIS_LOG_DIR=/app/logs
ENV AIS_SESSIONS_DIR=/app/sessions
ENV AIS_CHROMA_PATH=/app/memory/chroma

CMD ["python", "-m", "ais_os"]
