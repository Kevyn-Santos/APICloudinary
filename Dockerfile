FROM python:3.12-alpine3.22 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


FROM python:3.12-alpine3.22

LABEL authors="kevyn"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN adduser -D cloudinaryusr && \
    chown -R cloudinaryusr:cloudinaryusr /app
USER cloudinaryusr

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]
