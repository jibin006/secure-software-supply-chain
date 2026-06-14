# Stage 1 — Build
FROM python:3.12-slim@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9 AS builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2 — Runtime
FROM python:3.12-slim@sha256:a8140b6f78d9c94c6d6b3e7a5f4e2f9d8c3b1a0e7f6d5c4b3a2e1f0d9c8b7a6

WORKDIR /app

# OCI Labels for traceability
LABEL org.opencontainers.image.source="https://github.com/yourorg/secure-software-supply-chain"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.title="supply-chain-demo"

# Non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY app/ .

USER appuser

CMD ["python", "app.py"]