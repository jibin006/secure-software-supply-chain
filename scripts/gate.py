import json
import sys
from datetime import date

def load_scan_results(filepath):
    with open(filepath) as f:
        return json.load(f)

def load_policy(filepath="policies/supply-chain-policy.yaml"):
    import yaml
    with open(filepath) as f:
        return yaml.safe_load(f)

def evaluate_findings(results, policy):
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
    
    block_severities = policy.get("gate", {}).get("block_on", ["Critical", "High"])
    warn_severities = policy.get("gate", {}).get("warn_on", ["Medium"])
    
    for match in matches:
        vuln = match.get("vulnerability", {})
        severity = vuln.get("severity", "Unknown")
        cve_id = vuln.get("id", "UNKNOWN")
        package = match.get("artifact", {}).get("name", "unknown")
        version = match.get("artifact", {}).get("version", "unknown")
        fix_versions = vuln.get("fix", {}).get("versions", [])
        
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        finding = {
            "id": cve_id,
            "severity": severity,
            "package": package,
            "version": version,
            "fix": fix_versions[0] if fix_versions else "no fix available"
        }
        
        if severity in block_severities:
            blocking_findings.append(finding)
        elif severity in warn_severities:
            warning_findings.append(finding)
    
    return severity_counts, blocking_findings, warning_findings


def print_summary(severity_counts, blocking, warnings):
    print("\n" + "="*60)
    print("VULNERABILITY SCAN SUMMARY")
    print("="*60)
    
    for severity, count in severity_counts.items():
        if count > 0:
            marker = "🔴" if severity in ["Critical", "High"] else "🟡" if severity == "Medium" else "🟢"
            print(f"  {marker} {severity:<12}: {count}")
    
    if blocking:
        print(f"\n[GATE] BLOCKING findings ({len(blocking)}):")
        for f in blocking:
            print(f"  ❌ {f['id']} | {f['package']}=={f['version']}")
            print(f"     Severity: {f['severity']}")
            print(f"     Fix:      Upgrade to {f['fix']}")
            print()
    
    if warnings:
        print(f"\n[GATE] WARNING findings ({len(warnings)}):")
        for f in warnings:
            print(f"  ⚠️  {f['id']} | {f['package']}=={f['version']}")
            print(f"     Fix: Upgrade to {f['fix']}")
            print()


# Load policy
try:
    import yaml
    with open("policies/supply-chain-policy.yaml") as f:
        policy = yaml.safe_load(f)
except Exception:
    policy = {"gate": {"block_on": ["Critical", "High"], "warn_on": ["Medium"]}}

results = load_scan_results("scan-results/grype-results.json")
severity_counts, blocking, warnings = evaluate_findings(results, policy)
print_summary(severity_counts, blocking, warnings)

# Write enriched output for findings inventory
output = {
    "scan_date": str(date.today()),
    "severity_summary": severity_counts,
    "blocking_count": len(blocking),
    "warning_count": len(warnings),
    "gate_decision": "FAIL" if blocking else "PASS",
    "blocking_findings": blocking,
    "warning_findings": warnings
}

with open("scan-results/gate-decision.json", "w") as f:
    json.dump(output, f, indent=2)

if blocking:
    print(f"\n[GATE] Decision: FAIL")
    print(f"[GATE] {len(blocking)} Critical/High finding(s) block this build")
    print(f"[GATE] Fix vulnerabilities or add suppression with justification")
    sys.exit(1)

print(f"\n[GATE] Decision: PASS")
print(f"[GATE] No blocking vulnerabilities detected")