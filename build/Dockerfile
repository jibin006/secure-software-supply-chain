# Stage 1 — Build
FROM python:3.12-slim AS builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2 — Runtime
FROM python:3.12-slim

WORKDIR /app

# OCI Labels for traceability
LABEL org.opencontainers.image.source="https://github.com/jibin006/secure-software-supply-chain"
LABEL org.opencontainers.image.title="supply-chain-demo"

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY app/ .

USER appuser

CMD ["python", "app.py"]