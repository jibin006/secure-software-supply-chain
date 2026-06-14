#!/bin/bash
# Standalone verification script
# Run this to verify any image before trusting it

IMAGE="${1}"

if [ -z "${IMAGE}" ]; then
  echo "Usage: ./verify.sh <image:tag>"
  exit 1
fi

echo "[VERIFY] Verifying supply chain integrity for: ${IMAGE}"
echo ""

# Verify image signature
echo "[VERIFY] Step 1: Checking image signature"
if cosign verify \
  --certificate-identity-regexp="https://github.com/yourorg/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  "${IMAGE}" 2>/dev/null; then
  echo "[VERIFY] ✅ Signature valid"
else
  echo "[VERIFY] ❌ Signature invalid or missing"
  exit 1
fi

# Verify SBOM attestation
echo ""
echo "[VERIFY] Step 2: Checking SBOM attestation"
if cosign verify-attestation \
  --type cyclonedx \
  --certificate-identity-regexp="https://github.com/yourorg/.*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com" \
  "${IMAGE}" 2>/dev/null; then
  echo "[VERIFY] ✅ SBOM attestation valid"
else
  echo "[VERIFY] ⚠️  No SBOM attestation found"
fi

echo ""
echo "[VERIFY] Supply chain verification complete"