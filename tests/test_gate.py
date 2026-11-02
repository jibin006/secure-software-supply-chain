import datetime

from scripts.gate import evaluate_findings, is_suppressed, load_suppressions


def test_package_name_does_not_suppress_unlisted_cve():
    # A package-level allowlist must never suppress newly disclosed CVEs.
    assert is_suppressed("CVE-2099-0001", "libc6", []) is False


def test_exact_cve_package_suppression_with_future_expiry_is_accepted():
    suppressions = [{
        "id": "CVE-2099-0001",
        "package": "libc6",
        "justification": "No fix available yet",
        "approved_by": "security",
        "expires": "2099-12-31",
    }]
    assert is_suppressed("CVE-2099-0001", "libc6", suppressions) is True
    assert is_suppressed("CVE-2099-0002", "libc6", suppressions) is False
    assert is_suppressed("CVE-2099-0001", "perl-base", suppressions) is False


def test_expired_or_missing_expiry_never_suppresses():
    expired = [{
        "id": "CVE-2099-0001",
        "package": "libc6",
        "expires": "2000-01-01",
    }]
    missing = [{
        "id": "CVE-2099-0001",
        "package": "libc6",
    }]
    assert is_suppressed("CVE-2099-0001", "libc6", expired) is False
    assert is_suppressed("CVE-2099-0001", "libc6", missing) is False


def test_unknown_severity_is_blocked():
    results = {
        "matches": [{
            "vulnerability": {"id": "GHSA-unknown", "severity": "Unknown"},
            "artifact": {"name": "example", "version": "1.0"},
        }]
    }
    policy = {"gate": {"block_on": ["Critical", "High"], "warn_on": ["Medium"]}}
    (_, blocking, warnings, suppressed, active) = evaluate_findings(results, policy, [])
    assert len(blocking) == 1
    assert blocking[0]["severity"] == "Unknown"
    assert warnings == []
    assert suppressed == 0
    assert active == 1


def test_suppression_file_requires_expiry_and_approval_fields(tmp_path):
    path = tmp_path / "suppressions.yaml"
    path.write_text(
        "suppressions:\n"
        "  - id: CVE-2099-0001\n"
        "    package: libc6\n"
        "    justification: exception\n"
        "    approved_by: security\n",
        encoding="utf-8",
    )
    try:
        load_suppressions(str(path))
    except ValueError as exc:
        assert "expires" in str(exc)
    else:
        raise AssertionError("Suppression without expiry must be rejected")
