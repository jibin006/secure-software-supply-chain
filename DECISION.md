# Security Architecture Decision Log

## ADR-001: Digest Pinning

Decision:

Use digest-pinned base images.

Reason:

Tags are mutable and can change without source code modifications.

Benefit:

Reproducible builds and protection against tag mutation attacks.

---

## ADR-002: Policy-Based Deployment Gates

Decision:

Block deployments when Critical or High vulnerabilities exist.

Reason:

Prevent vulnerable artifacts from entering the trusted deployment lifecycle.

Benefit:

Security enforcement occurs automatically and consistently.

---

## ADR-003: Application-Owned Risk vs Platform-Owned Risk

Decision:

Suppress selected OS-level package findings.

Examples:

* libc6
* perl-base
* libsqlite3-0
* util-linux

Reason:

Project focus is application dependency governance.

OS package lifecycle is managed separately through base image maintenance processes.

Benefit:

Reduces alert fatigue and improves signal-to-noise ratio.

---

## ADR-004: Keyless Signing

Decision:

Use Cosign keyless signing with GitHub OIDC.

Reason:

Eliminates long-lived signing keys.

Benefit:

Stronger identity assurance and reduced key management overhead.

---

## ADR-005: Admission Control Enforcement

Decision:

Require valid signatures for production deployments.

Reason:

CI controls protect artifact creation.
Admission controls protect deployment.

Benefit:

Prevents CI bypass attacks.

---

## ADR-006: SBOM Generation

Decision:

Generate CycloneDX and SPDX SBOMs during every build.

Reason:

Maintain software inventory for future vulnerability analysis.

Benefit:

Rapid impact assessment when new vulnerabilities are disclosed.

---

## ADR-007: Risk Acceptance Workflow

Decision:

Support suppressions with expiration and ownership.

Reason:

Not every vulnerability can be remediated immediately.

Benefit:

Provides auditable exception handling while preserving security governance.
