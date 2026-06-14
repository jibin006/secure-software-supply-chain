import json
import sys
from datetime import date, datetime
import yaml

SUPPRESSED_PACKAGES = {
    "python",
    "libc6",
    "libc-bin",
    "perl-base",
    "libncursesw6",
    "libtinfo6",
    "ncurses-base",
    "ncurses-bin",
    "liblzma5",
    "libbz2-1.0",
    "libsqlite3-0",
    "bsdutils",
    "libblkid1",
    "liblastlog2-2",
    "libmount1",
    "libsmartcols1",
    "libuuid1",
    "login",
    "mount",
    "util-linux",
    "tar",
    "zlib1g"
}


def load_scan_results(filepath):
    with open(filepath) as f:
        return json.load(f)


def load_policy(filepath="policies/supply-chain-policy.yaml"):
    with open(filepath) as f:
        return yaml.safe_load(f)


def load_suppressions(filepath="policies/suppressions.yaml"):
    try:
        with open(filepath) as f:
            data = yaml.safe_load(f)
            return data.get("suppressions", [])
    except FileNotFoundError:
        return []


def is_suppressed(cve_id, package, suppressions):

    # Package-level suppression
    if package in SUPPRESSED_PACKAGES:
        return True

    # Explicit CVE suppressions
    for item in suppressions:

        if (
            item.get("id") == cve_id
            and item.get("package") == package
        ):

            expiry = item.get("expires")

            if expiry:
                try:
                    expiry_date = datetime.strptime(
                        expiry,
                        "%Y-%m-%d"
                    ).date()

                    if expiry_date < date.today():
                        print(
                            f"[SUPPRESSION] EXPIRED: "
                            f"{cve_id} ({package})"
                        )
                        return False

                except ValueError:
                    print(
                        f"[SUPPRESSION] Invalid expiry "
                        f"date for {cve_id}"
                    )
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
        .get("block_on", ["Critical", "High"])
    )

    warn_severities = (
        policy.get("gate", {})
        .get("warn_on", ["Medium"])
    )

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


# Main

try:
    policy = load_policy()
except Exception:
    policy = {
        "gate": {
            "block_on": [
                "Critical",
                "High"
            ],
            "warn_on": [
                "Medium"
            ]
        }
    }

suppressions = load_suppressions()

results = load_scan_results(
    "scan-results/grype-results.json"
)

(
    severity_counts,
    blocking,
    warnings,
    suppressed_count,
    active_count
) = evaluate_findings(
    results,
    policy,
    suppressions
)

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
    "gate_decision": (
        "FAIL"
        if blocking
        else "PASS"
    ),
    "blocking_findings": blocking,
    "warning_findings": warnings
}

with open(
    "scan-results/gate-decision.json",
    "w"
) as f:
    json.dump(output, f, indent=2)

if blocking:

    print("\n[GATE] Decision: FAIL")

    print(
        f"[GATE] "
        f"{len(blocking)} Critical/High "
        f"finding(s) block this build"
    )

    print(
        "[GATE] Fix vulnerabilities "
        "or add approved suppression"
    )

    sys.exit(1)

print("\n[GATE] Decision: PASS")
print(
    "[GATE] No blocking "
    "vulnerabilities detected"
)