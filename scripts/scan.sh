#!/bin/bash
set -e

SBOM_FILE="sbom/sbom.cyclonedx.json"
SCAN_OUTPUT="scan-results/grype-results.json"
SCAN_TABLE="scan-results/grype-table.txt"

mkdir -p scan-results

echo "[SCAN] Installing Grype"
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

echo "[SCAN] Scanning SBOM for vulnerabilities"

# Generate JSON output for processing
grype "sbom:${SBOM_FILE}" \
  --output json \
  --file "${SCAN_OUTPUT}"

# Generate human-readable table
grype "sbom:${SBOM_FILE}" \
  --output table \
  --file "${SCAN_TABLE}"

cat "${SCAN_TABLE}"

echo ""
echo "[SCAN] Applying severity gate"

python3 scripts/gate.py