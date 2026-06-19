FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt 2>/dev/null || \
    pip install --no-cache-dir --timeout 120 fastapi uvicorn pydantic pandas numpy scikit-learn

FROM python:3.13-slim

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r mlservice \
    && useradd -r -g mlservice -d /app -s /sbin/nologin mlservice

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

COPY . .

RUN mkdir -p /app/data/raw /app/data/processed /app/data/models /app/logs \
    && chown -R mlservice:mlservice /app

USER mlservice

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]