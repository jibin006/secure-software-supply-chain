#!/bin/bash
set -e

IMAGE_NAME="${FULL_IMAGE:-supply-chain-demo:local}"
SBOM_DIR="sbom"
SBOM_FILE="${SBOM_DIR}/sbom.cyclonedx.json"
SBOM_SPDX="${SBOM_DIR}/sbom.spdx.json"

mkdir -p "${SBOM_DIR}"

echo "[SBOM] Installing Syft"
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

echo "[SBOM] Generating CycloneDX SBOM"
syft "${IMAGE_NAME}" \
  --output cyclonedx-json="${SBOM_FILE}" \
  --output spdx-json="${SBOM_SPDX}"

echo "[SBOM] SBOM generated successfully"

# Show component count
COMPONENT_COUNT=$(python3 -c "
import json
with open('${SBOM_FILE}') as f:
    data = json.load(f)
print(len(data.get('components', [])))
")

echo "[SBOM] Components identified: ${COMPONENT_COUNT}"

# Extract and display Python packages specifically
python3 - <<'EOF'
import json

with open("sbom/sbom.cyclonedx.json") as f:
    sbom = json.load(f)

components = sbom.get("components", [])
python_pkgs = [c for c in components if c.get("type") == "library"]

print(f"\n[SBOM] Library components found: {len(python_pkgs)}")
print(f"\n{'Package':<30} {'Version':<15} {'PURL'}")
print("-" * 80)

for pkg in python_pkgs[:20]:
    name = pkg.get("name", "unknown")
    version = pkg.get("version", "unknown")
    purl = pkg.get("purl", "")[:40]
    print(f"{name:<30} {version:<15} {purl}")
EOF