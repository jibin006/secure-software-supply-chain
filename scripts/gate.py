import json
import sys
from datetime import date, datetime
import yaml



def load_scan_results(filepath):
    with open(filepath) as f:
        return json.load(f)


def load_policy(filepath="policies/supply-chain-policy.yaml"):
    with open(filepath, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or not isinstance(data.get("gate"), dict):
        raise ValueError("Supply-chain policy must contain a gate mapping")

    gate = data["gate"]
    for key in ("block_on", "warn_on"):
        if not isinstance(gate.get(key), list):
            raise ValueError(f"Policy gate.{key} must be a list")
    return data


def load_suppressions(filepath="policies/suppressions.yaml"):
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return []

    if not isinstance(data, dict) or not isinstance(data.get("suppressions", []), list):
        raise ValueError("Suppression file must contain a suppressions list")

    required = ("id", "package", "justification", "approved_by", "expires")
    for index, item in enumerate(data.get("suppressions", [])):
        if not isinstance(item, dict):
            raise ValueError(f"Suppression entry {index} must be a mapping")
        missing = [field for field in required if not item.get(field)]
        if missing:
            raise ValueError(f"Suppression entry {index} is missing required fields: {missing}")
        try:
            datetime.strptime(item["expires"], "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(
                f"Suppression entry {index} has invalid expires date; expected YYYY-MM-DD"
            ) from exc
    return data.get("suppressions", [])


def is_suppressed(cve_id, package, suppressions):
    """Only an exact CVE + package + unexpired approval can suppress a finding."""
    for item in suppressions:
        if item.get("id") != cve_id or item.get("package") != package:
            continue

        expiry = item.get("expires")
        if not expiry:
            print(f"[SUPPRESSION] REJECTED: {cve_id} ({package}) has no expiry")
            return False

        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        except ValueError:
            print(f"[SUPPRESSION] REJECTED: invalid expiry for {cve_id} ({package})")
            return False

        if expiry_date < date.today():
            print(f"[SUPPRESSION] EXPIRED: {cve_id} ({package})")
            return False

        return True

    return False

def evaluate_findings(results, policy, suppressions):
    matches = results.get("matches", [])

    severity_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0,
        "Negligible": 0,
        "Unknown": 0
    }

    blocking_findings = []
    warning_findings = []

    suppressed_count = 0
    active_count = 0

    block_severities = (
        policy.get("gate", {})
        .get("block_on", ["Critical", "High", "Unknown"])
    )

    warn_severities = (
        policy.get("gate", {})
        .get("warn_on", ["Medium"])
    )
    # Unknown/unmapped severities must never become an implicit pass.
    block_severities = set(block_severities) | {"Unknown"}

    for match in matches:

        vuln = match.get("vulnerability", {})
        severity = vuln.get("severity", "Unknown")
        cve_id = vuln.get("id", "UNKNOWN")

        artifact = match.get("artifact", {})
        package = artifact.get("name", "unknown")
        version = artifact.get("version", "unknown")

        fix_versions = (
            vuln.get("fix", {})
            .get("versions", [])
        )

        if is_suppressed(
            cve_id,
            package,
            suppressions
        ):
            suppressed_count += 1
            continue

        active_count += 1

        severity_counts[severity] = (
            severity_counts.get(severity, 0) + 1
        )

        finding = {
            "id": cve_id,
            "severity": severity,
            "package": package,
            "version": version,
            "fix": (
                fix_versions[0]
                if fix_versions
                else "no fix available"
            )
        }

        if severity in block_severities:
            blocking_findings.append(finding)

        elif severity in warn_severities:
            warning_findings.append(finding)

    return (
        severity_counts,
        blocking_findings,
        warning_findings,
        suppressed_count,
        active_count
    )


def print_summary(
    severity_counts,
    blocking,
    warnings,
    suppressed_count,
    active_count
):

    print("\n" + "=" * 60)
    print("VULNERABILITY SCAN SUMMARY")
    print("=" * 60)

    print(
        f"Suppressed Findings : {suppressed_count}"
    )

    print(
        f"Active Findings     : {active_count}"
    )

    print("")

    for severity, count in severity_counts.items():
        if count > 0:

            marker = (
                "🔴"
                if severity in ["Critical", "High"]
                else "🟡"
                if severity == "Medium"
                else "🟢"
            )

            print(
                f"  {marker} "
                f"{severity:<12}: {count}"
            )

    if blocking:

        print(
            f"\n[GATE] BLOCKING findings "
            f"({len(blocking)}):"
        )

        for f in blocking:

            print(
                f"  ❌ {f['id']} | "
                f"{f['package']}=={f['version']}"
            )

            print(
                f"     Severity: "
                f"{f['severity']}"
            )

            print(
                f"     Fix: Upgrade to "
                f"{f['fix']}"
            )

            print()

    if warnings:

        print(
            f"\n[GATE] WARNING findings "
            f"({len(warnings)}):"
        )

        for f in warnings:

            print(
                f"  ⚠️  {f['id']} | "
                f"{f['package']}=={f['version']}"
            )

            print(
                f"     Fix: Upgrade to "
                f"{f['fix']}"
            )

            print()




def main():
    policy = load_policy()
    suppressions = load_suppressions()

    results = load_scan_results("scan-results/grype-results.json")

    (
        severity_counts,
        blocking,
        warnings,
        suppressed_count,
        active_count
    ) = evaluate_findings(results, policy, suppressions)

    print_summary(
        severity_counts,
        blocking,
        warnings,
        suppressed_count,
        active_count
    )

    output = {
        "scan_date": str(date.today()),
        "severity_summary": severity_counts,
        "suppressed_findings": suppressed_count,
        "active_findings": active_count,
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
        "gate_decision": "FAIL" if blocking else "PASS",
        "blocking_findings": blocking,
        "warning_findings": warnings
    }

    with open("scan-results/gate-decision.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    if blocking:
        print("\\n[GATE] Decision: FAIL")
        print(f"[GATE] {len(blocking)} Critical/High/Unknown finding(s) block this build")
        print("[GATE] Fix vulnerabilities or add an approved, CVE-specific suppression")
        sys.exit(1)

    print("\\n[GATE] Decision: PASS")
    print("[GATE] No blocking vulnerabilities detected")


if __name__ == "__main__":
    main()
