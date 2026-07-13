import argparse
import json
import tomllib
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    """Load a JSON document from disk."""
    with file_path.open(encoding="utf-8") as file:
        return json.load(file)


def load_policy(file_path: Path) -> dict[str, Any]:
    """Load a TOML policy document from disk."""
    with file_path.open("rb") as file:
        return tomllib.load(file)


def evaluate_trivy_evidence(
    policy: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate normalized Trivy evidence against a release policy."""
    policy_metadata = policy["policy"]
    controls = policy["controls"]["trivy"]

    findings = evidence.get("findings", {})
    evidence_metadata = evidence.get("evidence", {})

    critical = findings.get("critical", 0)
    high = findings.get("high", 0)
    medium = findings.get("medium", 0)

    blocking_findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    evidence_is_valid = evidence_metadata.get("valid", False)

    if controls["require_valid_evidence"] and not evidence_is_valid:
        blocking_findings.append(
            {
                "control_id": "ARG-EVIDENCE-001",
                "message": "Required scanner evidence is invalid.",
                "actual": evidence_is_valid,
                "expected": True,
            }
        )

    if critical > controls["maximum_critical"]:
        blocking_findings.append(
            {
                "control_id": "ARG-SECURITY-001",
                "message": "Critical vulnerabilities exceed policy.",
                "actual": critical,
                "expected_maximum": controls["maximum_critical"],
            }
        )

    if high > controls["maximum_high"]:
        blocking_findings.append(
            {
                "control_id": "ARG-SECURITY-002",
                "message": "High vulnerabilities exceed policy.",
                "actual": high,
                "expected_maximum": controls["maximum_high"],
            }
        )

    if controls["medium_findings_generate_warning"] and medium > 0:
        warnings.append(
            {
                "control_id": "ARG-SECURITY-003",
                "message": "Medium vulnerabilities require attention.",
                "actual": medium,
                "expected": 0,
            }
        )

    if blocking_findings:
        decision = "FAIL"
    elif warnings:
        decision = "WARNING"
    else:
        decision = "PASS"

    return {
        "policy": {
            "id": policy_metadata["id"],
            "name": policy_metadata["name"],
            "version": policy_metadata["version"],
        },
        "scanner": evidence.get("scanner"),
        "scanner_report_id": evidence.get("report_id"),
        "source": evidence.get("source", {}),
        "decision": decision,
        "blocking_findings": blocking_findings,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate normalized security evidence."
    )
    parser.add_argument(
        "--policy",
        required=True,
        help="Path to the TOML release policy.",
    )
    parser.add_argument(
        "--evidence",
        required=True,
        help="Path to the normalized scanner evidence.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the governance decision.",
    )

    args = parser.parse_args()

    policy = load_policy(Path(args.policy))
    evidence = load_json(Path(args.evidence))

    decision = evaluate_trivy_evidence(policy, evidence)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(decision, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
