#!/bin/bash
set -e

IMAGE_NAME="supply-chain-demo"
IMAGE_TAG="${GITHUB_SHA:-local}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "[BUILD] Building secure container image"
echo "[BUILD] Image: ${FULL_IMAGE}"

docker build \
  --file build/Dockerfile \
  --tag "${FULL_IMAGE}" \
  --label "org.opencontainers.image.revision=${IMAGE_TAG}" \
  --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  .

echo "[BUILD] Image built successfully"
echo "[BUILD] Digest: $(docker inspect ${FULL_IMAGE} --format='{{index .RepoDigests 0}}' 2>/dev/null || echo 'local build')"

# Export for subsequent steps
echo "IMAGE_TAG=${IMAGE_TAG}" >> "${GITHUB_ENV:-/dev/null}" 2>/dev/null || true
echo "FULL_IMAGE=${FULL_IMAGE}" >> "${GITHUB_ENV:-/dev/null}" 2>/dev/null || true