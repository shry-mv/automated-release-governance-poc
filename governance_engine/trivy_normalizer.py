import argparse
import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    """Load a JSON document from disk."""
    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


def validate_report(report: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate that the report contains essential audit metadata."""
    required_values = {
        "SchemaVersion": report.get("SchemaVersion"),
        "Trivy.Version": report.get("Trivy", {}).get("Version"),
        "ReportID": report.get("ReportID"),
        "CreatedAt": report.get("CreatedAt"),
        "ArtifactID": report.get("ArtifactID"),
        "ArtifactName": report.get("ArtifactName"),
        "ArtifactType": report.get("ArtifactType"),
    }

    missing_fields = [
        field_name
        for field_name, value in required_values.items()
        if value is None or value == ""
    ]

    return len(missing_fields) == 0, missing_fields


def count_findings(report: dict[str, Any]) -> dict[str, int]:
    """Count Trivy vulnerabilities by severity."""
    counts = {
        "UNKNOWN": 0,
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    results = report.get("Results", [])

    for result in results:
        vulnerabilities = result.get("Vulnerabilities") or []

        for vulnerability in vulnerabilities:
            severity = vulnerability.get("Severity", "UNKNOWN").upper()

            if severity not in counts:
                severity = "UNKNOWN"

            counts[severity] += 1

    return counts


def determine_status(counts: dict[str, int]) -> str:
    """Create an initial scanner status from vulnerability counts."""
    if counts["CRITICAL"] > 0 or counts["HIGH"] > 0:
        return "FAIL"

    if counts["MEDIUM"] > 0:
        return "WARNING"

    return "PASS"


def normalize_report(report: dict[str, Any]) -> dict[str, Any]:
    """Convert a Trivy report into the portfolio's normalized format."""
    counts = count_findings(report)
    metadata = report.get("Metadata", {})

    evidence_valid, missing_fields = validate_report(report)
    results_present = "Results" in report
    total_findings = sum(counts.values())

    if not evidence_valid:
        status = "FAIL"
        decision_reason = "Required audit metadata is missing."
        report_state = "INVALID_EVIDENCE"
    else:
        status = determine_status(counts)

        if total_findings > 0:
            report_state = "FINDINGS_REPORTED"
            decision_reason = "Security findings were evaluated."
        else:
            report_state = "NO_FINDINGS_REPORTED"
            decision_reason = "The report is valid and contains no reported findings."

    return {
        "scanner": "trivy",
        "scanner_version": report.get("Trivy", {}).get("Version", "unknown"),
        "report_id": report.get("ReportID"),
        "created_at": report.get("CreatedAt"),
        "artifact": {
            "name": report.get("ArtifactName"),
            "type": report.get("ArtifactType"),
            "id": report.get("ArtifactID"),
        },
        "source": {
            "repository": metadata.get("RepoURL"),
            "branch": metadata.get("Branch"),
            "commit": metadata.get("Commit"),
        },
        "evidence": {
            "valid": evidence_valid,
            "missing_fields": missing_fields,
            "results_property_present": results_present,
            "report_state": report_state,
        },
        "findings": {
            "critical": counts["CRITICAL"],
            "high": counts["HIGH"],
            "medium": counts["MEDIUM"],
            "low": counts["LOW"],
            "unknown": counts["UNKNOWN"],
        },
        "status": status,
        "decision_reason": decision_reason,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize a Trivy JSON security report."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the original Trivy JSON report.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the normalized JSON result.",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    report = load_json(input_path)
    normalized = normalize_report(report)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(normalized, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(normalized, indent=2))


if __name__ == "__main__":
    main()
