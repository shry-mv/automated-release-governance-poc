from governance_engine.trivy_normalizer import (
    count_findings,
    determine_status,
    normalize_report,
    validate_report,
)


def test_count_findings_by_severity() -> None:
    report = {
        "Results": [
            {
                "Vulnerabilities": [
                    {"Severity": "CRITICAL"},
                    {"Severity": "HIGH"},
                    {"Severity": "HIGH"},
                    {"Severity": "MEDIUM"},
                    {"Severity": "LOW"},
                ]
            }
        ]
    }

    counts = count_findings(report)

    assert counts["CRITICAL"] == 1
    assert counts["HIGH"] == 2
    assert counts["MEDIUM"] == 1
    assert counts["LOW"] == 1
    assert counts["UNKNOWN"] == 0


def test_status_is_fail_when_high_vulnerability_exists() -> None:
    counts = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 0,
        "LOW": 0,
        "UNKNOWN": 0,
    }

    assert determine_status(counts) == "FAIL"


def test_status_is_warning_when_only_medium_exists() -> None:
    counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 2,
        "LOW": 0,
        "UNKNOWN": 0,
    }

    assert determine_status(counts) == "WARNING"


def test_valid_report_without_results_is_pass() -> None:
    report = {
        "SchemaVersion": 2,
        "Trivy": {"Version": "0.70.0"},
        "ReportID": "demo-report-001",
        "CreatedAt": "2026-07-13T00:47:07Z",
        "ArtifactID": "sha256:demo123",
        "ArtifactName": ".",
        "ArtifactType": "repository",
        "Metadata": {
            "RepoURL": "https://github.com/example/repository",
            "Branch": "main",
            "Commit": "abc123",
        },
    }

    normalized = normalize_report(report)

    assert normalized["scanner"] == "trivy"
    assert normalized["evidence"]["valid"] is True
    assert normalized["evidence"]["results_property_present"] is False
    assert normalized["evidence"]["report_state"] == "NO_FINDINGS_REPORTED"
    assert normalized["findings"]["critical"] == 0
    assert normalized["status"] == "PASS"


def test_invalid_report_fails_closed() -> None:
    report = {
        "SchemaVersion": 2,
        "Trivy": {"Version": "0.70.0"},
        "ArtifactName": ".",
        "ArtifactType": "repository",
    }

    normalized = normalize_report(report)

    assert normalized["evidence"]["valid"] is False
    assert normalized["evidence"]["report_state"] == "INVALID_EVIDENCE"
    assert normalized["status"] == "FAIL"
    assert "ReportID" in normalized["evidence"]["missing_fields"]
    assert "CreatedAt" in normalized["evidence"]["missing_fields"]
    assert "ArtifactID" in normalized["evidence"]["missing_fields"]


def test_validate_report_accepts_complete_metadata() -> None:
    report = {
        "SchemaVersion": 2,
        "Trivy": {"Version": "0.70.0"},
        "ReportID": "report-001",
        "CreatedAt": "2026-07-13T00:47:07Z",
        "ArtifactID": "sha256:demo123",
        "ArtifactName": ".",
        "ArtifactType": "repository",
    }

    evidence_valid, missing_fields = validate_report(report)

    assert evidence_valid is True
    assert missing_fields == []
