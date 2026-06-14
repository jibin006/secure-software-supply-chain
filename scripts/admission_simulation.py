"""
Admission Controller Simulation
Demonstrates the logic of a Kubernetes admission webhook
without requiring a live cluster.
"""

import json
import sys

def verify_image_signature(image: str, signed_images: list) -> dict:
    """
    Simulates cosign verify check
    In production this calls the actual Sigstore verification
    """
    is_signed = image in signed_images
    
    return {
        "image": image,
        "signed": is_signed,
        "issuer": "https://token.actions.githubusercontent.com" if is_signed else None,
        "transparency_log": "rekor.sigstore.dev" if is_signed else None
    }

def admission_decision(deployment_request: dict, signed_images: list) -> dict:
    """
    Simulates Kubernetes admission webhook decision
    """
    image = deployment_request.get("image")
    namespace = deployment_request.get("namespace")
    
    print(f"\n[ADMISSION] Evaluating deployment request")
    print(f"  Image:     {image}")
    print(f"  Namespace: {namespace}")
    
    # Check policy applies to this namespace
    if namespace != "production":
        return {
            "decision": "ALLOW",
            "reason": f"Policy not enforced in namespace: {namespace}"
        }
    
    # Verify signature
    verification = verify_image_signature(image, signed_images)
    
    if not verification["signed"]:
        return {
            "decision": "DENY",
            "reason": f"Image {image} has no valid Cosign signature. "
                     f"Only signed images are permitted in production. "
                     f"Sign the image via your CI pipeline before deploying."
        }
    
    return {
        "decision": "ALLOW",
        "reason": f"Image signature verified via {verification['issuer']}. "
                 f"Recorded in {verification['transparency_log']}."
    }


# Simulate signed image registry
SIGNED_IMAGES = [
    "ghcr.io/jibin006/supply-chain-demo:abc123",
    "ghcr.io/jibin006/api-service:def456"
]

# Test scenarios
scenarios = [
    {
        "name": "Scenario 1: Signed image to production",
        "request": {
            "image": "ghcr.io/jibin006/supply-chain-demo:abc123",
            "namespace": "production"
        }
    },
    {
        "name": "Scenario 2: Unsigned image to production",
        "request": {
            "image": "ghcr.io/jibin006/supply-chain-demo:latest",
            "namespace": "production"
        }
    },
    {
        "name": "Scenario 3: Unsigned image to development",
        "request": {
            "image": "ghcr.io/jibin006/supply-chain-demo:dev-branch",
            "namespace": "development"
        }
    }
]

print("="*60)
print("ADMISSION CONTROLLER SIMULATION")
print("="*60)

for scenario in scenarios:
    print(f"\n{'='*60}")
    print(f"TEST: {scenario['name']}")
    
    decision = admission_decision(scenario["request"], SIGNED_IMAGES)
    
    status = "✅ ALLOWED" if decision["decision"] == "ALLOW" else "❌ DENIED"
    print(f"\n[DECISION] {status}")
    print(f"[REASON]   {decision['reason']}")

print(f"\n{'='*60}")
print("Simulation complete")
print("In production: Sigstore Policy Controller enforces this")
print("automatically as a Kubernetes admission webhook")