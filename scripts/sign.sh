#!/bin/bash
set -e

IMAGE="${FULL_IMAGE:-supply-chain-demo:local}"
REGISTRY_IMAGE="${REGISTRY:-ghcr.io/yourorg}/${IMAGE}"

echo "[SIGN] Installing Cosign"
curl -sSfL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 \
  -o /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign

echo "[SIGN] Signing image with keyless OIDC"
echo "[SIGN] Image: ${REGISTRY_IMAGE}"

# Keyless signing using GitHub Actions OIDC token
cosign sign \
  --yes \
  "${REGISTRY_IMAGE}"

echo "[SIGN] Attaching SBOM attestation"

# Attach SBOM as attestation
cosign attest \
  --yes \
  --predicate sbom/sbom.cyclonedx.json \
  --type cyclonedx \
  "${REGISTRY_IMAGE}"

echo "[SIGN] Verifying signature immediately after signing"

cosign verify \
  --certificate-identity-regexp="https://github.com/yourorg/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  "${REGISTRY_IMAGE}" | python3 -m json.tool

echo "[SIGN] Signature verified successfully"
echo "[SIGN] Transparency log entry recorded in Rekor"