# Secure Software Supply Chain Platform

## Overview

Built an end-to-end Software Supply Chain Security Platform that prevents vulnerable or untrusted container images from reaching production.

The platform automatically builds container images, generates Software Bills of Materials (SBOMs), scans for vulnerabilities, enforces policy-based deployment gates, signs trusted artifacts using Sigstore Cosign, and validates image trust before deployment through Kubernetes admission control policies.

This project demonstrates how modern platform and cloud security teams implement secure-by-default CI/CD pipelines and enforce software supply chain trust at deployment time.

---

## Architecture

Developer Commit
→ Secure Container Build
→ SBOM Generation (Syft)
→ Vulnerability Scanning (Grype)
→ Policy Gate Evaluation
→ Cosign Keyless Signing
→ Signature Verification
→ Kubernetes Admission Control
→ Deployment Decision

---

## Security Controls Implemented

### 1. Container Image Hardening

* Multi-stage Docker builds
* Non-root container execution
* Minimal runtime image
* Digest-pinned base image
* OCI metadata labeling

### 2. Software Bill of Materials (SBOM)

Generated SBOMs using Syft to provide complete software component visibility.

Benefits:

* Dependency inventory
* Software provenance
* Compliance evidence
* Vulnerability correlation

### 3. Vulnerability Scanning

Integrated Grype into the CI/CD pipeline to scan:

* Application dependencies
* Python packages
* Operating system packages
* Base image components

Findings are categorized into:

* Critical
* High
* Medium
* Low
* Negligible

### 4. Policy-Based Security Gates

Custom Python policy engine evaluates scan results and blocks deployments when risk thresholds are exceeded.

Gate Policy:

* Block on Critical vulnerabilities
* Block on High vulnerabilities
* Warn on Medium vulnerabilities

Example:

```text
[GATE] Decision: FAIL
[GATE] 8 Critical/High findings block this build
```

### 5. Risk Acceptance & CVE-Specific Suppressions

Implemented suppression management with:

* CVE tracking
* Justification requirements
* Expiration dates
* Security ownership

This simulates how enterprise platform security teams manage accepted risks while maintaining auditability.

### 6. Sigstore Cosign Signing

Implemented keyless image signing using:

* GitHub OIDC
* Sigstore Fulcio
* Rekor Transparency Log

Benefits:

* Cryptographic integrity
* Artifact authenticity
* Build provenance validation

### 7. Signature Verification

Images are verified before deployment to ensure:

* Trusted build source
* Valid signature
* Provenance integrity

### 8. Kubernetes Admission Control

Simulated Kubernetes admission controller behavior to enforce:

* Signed image requirements
* Namespace-based policy enforcement
* Production deployment protection

---

## Project Structure

```text
secure-software-supply-chain/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── build/
│   ├── Dockerfile
│   └── Dockerfile.insecure
│
├── admission/
│   └── cluster-image-policy.yaml
│
├── policies/
│   ├── supply-chain-policy.yaml
│   └── suppressions.yaml
│
├── scripts/
│   ├── gate.py
│   ├── build.sh
│   ├── scan.sh
│   ├── sign.sh
│   ├── generate_sbom.sh
│   └── admission_simulation.py
│
├── signing/
│   └── verify.sh
│
└── .github/workflows/
    └── supply-chain.yml
```

---

## CI/CD Security Workflow

### Vulnerable Dependency Scenario

```text
Developer Commit
        ↓
Build Container
        ↓
Generate SBOM
        ↓
Scan Vulnerabilities
        ↓
Policy Evaluation
        ↓
FAIL
        ↓
Deployment Blocked
```

### Secure Dependency Scenario

```text
Developer Commit
        ↓
Build Container
        ↓
Generate SBOM
        ↓
Scan Vulnerabilities
        ↓
PASS
        ↓
Cosign Sign
        ↓
Verify Signature
        ↓
Admission Approval
        ↓
Deploy
```

---

## Sample Admission Decisions

### Signed Image

```text
Image: ghcr.io/jibin006/supply-chain-demo:abc123

Decision: ALLOWED
Reason: Valid Cosign signature verified
```

### Unsigned Image

```text
Image: ghcr.io/jibin006/supply-chain-demo:latest

Decision: DENIED
Reason: No valid signature found
```

---

## Technologies Used

### Security

* Syft
* Grype
* Cosign
* Sigstore
* Rekor
* OIDC

### Cloud Native

* Docker
* Kubernetes
* Admission Policies
* OCI Images

### DevSecOps

* GitHub Actions
* Policy as Code
* CI/CD Security Gates

### Programming

* Python
* YAML
* Shell Scripting

---

## Key Security Concepts Demonstrated

* Software Supply Chain Security
* Secure CI/CD Pipelines
* SBOM Generation
* Vulnerability Management
* Risk Acceptance Workflows
* Policy-as-Code
* Cryptographic Artifact Signing
* OIDC-Based Trust
* Kubernetes Admission Control
* Deployment Trust Enforcement

---

## Business Impact

This platform prevents vulnerable or untrusted software artifacts from reaching production environments by enforcing automated security controls throughout the software delivery lifecycle.

The approach reduces software supply chain risk, improves deployment trust, and enables security teams to implement scalable security governance without slowing developer productivity.
