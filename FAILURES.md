# Security Validation Scenarios

This document demonstrates how the platform behaves when trust assumptions are violated.

---

## Scenario 1 — Vulnerable Dependency

State:

requirements.txt contains:

* urllib3==1.24.3
* requests==2.20.0
* flask==0.12.2

Result:

Build
↓
SBOM
↓
Scan
↓
Policy Gate
↓
FAIL

Example:

[GATE] Decision: FAIL

Reason:

High-severity vulnerabilities detected in application-owned dependencies.

Security Outcome:

Deployment blocked before signing.

---

## Scenario 2 — Unsigned Image Deployment

State:

Image exists but has no valid Cosign signature.

Result:

Admission Controller
↓
DENY

Example:

[DECISION] DENIED

Reason:

No valid image signature found.

Security Outcome:

Unsigned artifacts cannot reach production.

---

## Scenario 3 — Mutable Tag Attack

State:

Dockerfile changed from:

FROM python:3.12-slim@sha256:<digest>

to:

FROM python:3.12-slim

Result:

Same source code
↓
Different base image
↓
Different vulnerability profile

Observed:

New SQLite vulnerabilities appeared without application changes.

Security Outcome:

Demonstrated tag mutation risk.

Lesson:

Tags are mutable.
Digests are immutable.

Digest pinning guarantees reproducible builds.

---

## Scenario 4 — SBOM Query Simulation

State:

New critical vulnerability announced for libsqlite3-0.

Action:

Query previously generated SBOM.

Example:

jq '.components[] | select(.name | contains("sqlite"))' sbom/sbom.cyclonedx.json

Result:

Package identified immediately.

Security Outcome:

Impact assessment completed without rebuilding or rescanning images.

Lesson:

SBOMs transform vulnerability response from discovery mode into query mode.

---

## Scenario 5 — Registry Trust vs Build Trust

State:

Attacker pushes image directly to registry.

Question:

Can it deploy?

Result:

No.

Admission Controller rejects the image because no valid signature exists.

Lesson:

Registry trust is not build trust.

Only artifacts produced by approved CI workflows become deployable.
