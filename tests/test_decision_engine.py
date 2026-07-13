from typing import Any

from governance_engine.decision_engine import evaluate_trivy_evidence


def create_policy() -> dict[str, Any]:
    return {
        "policy": {
            "id": "ARG-POL-001",
            "name": "Repository Security Release Policy",
            "version": "1.0.0",
            "fail_closed": True,
        },
        "controls": {
            "trivy": {
                "require_valid_evidence": True,
                "maximum_critical": 0,
                "maximum_high": 0,
                "medium_findings_generate_warning": True,
            }
        },
    }


def create_evidence(
    *,
    valid: bool = True,
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
) -> dict[str, Any]:
    return {
        "scanner": "trivy",
        "report_id": "report-demo-001",
        "source": {
            "repository": "https://github.com/example/repository",
            "branch": "main",
            "commit": "abc123",
        },
        "evidence": {
            "valid": valid,
        },
        "findings": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": 0,
            "unknown": 0,
        },
    }


def test_decision_is_pass_when_controls_are_satisfied() -> None:
    policy = create_policy()
    evidence = create_evidence()

    result = evaluate_trivy_evidence(policy, evidence)

    assert result["decision"] == "PASS"
    assert result["blocking_findings"] == []
    assert result["warnings"] == []


def test_decision_is_warning_for_medium_findings() -> None:
    policy = create_policy()
    evidence = create_evidence(medium=2)

    result = evaluate_trivy_evidence(policy, evidence)

    assert result["decision"] == "WARNING"
    assert result["blocking_findings"] == []
    assert result["warnings"][0]["control_id"] == "ARG-SECURITY-003"


def test_decision_is_fail_for_critical_findings() -> None:
    policy = create_policy()
    evidence = create_evidence(critical=1)

    result = evaluate_trivy_evidence(policy, evidence)

    assert result["decision"] == "FAIL"
    assert result["blocking_findings"][0]["control_id"] == "ARG-SECURITY-001"


def test_decision_is_fail_for_high_findings() -> None:
    policy = create_policy()
    evidence = create_evidence(high=3)

    result = evaluate_trivy_evidence(policy, evidence)

    assert result["decision"] == "FAIL"
    assert result["blocking_findings"][0]["control_id"] == "ARG-SECURITY-002"


def test_decision_fails_closed_when_evidence_is_invalid() -> None:
    policy = create_policy()
    evidence = create_evidence(valid=False)

    result = evaluate_trivy_evidence(policy, evidence)

    assert result["decision"] == "FAIL"
    assert result["blocking_findings"][0]["control_id"] == "ARG-EVIDENCE-001"
