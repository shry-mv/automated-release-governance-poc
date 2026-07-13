# Portfolio Demo Guide

## Demo objective

Demonstrate how distributed quality and security evidence is converted into a single, explainable and enforceable release decision.

## Suggested five-minute walkthrough

### 1. Show the repository

Explain the separation between:

- Sample application.
- Tests.
- Governance engine.
- Version-controlled policy.
- GitHub Actions workflows.

### 2. Show the quality controls

Open the Quality Gate workflow and show:

- Ruff validation.
- Formatting validation.
- Unit tests.
- Coverage enforcement.
- Dependency vulnerability audit.

### 3. Show the security controls

Open:

- CodeQL Advanced.
- Trivy Security Scan.

Explain that CodeQL performs static security analysis while Trivy evaluates repository dependencies, secrets and configuration.

### 4. Show the evidence chain

Download or display:

- `trivy-results.json`
- `trivy-summary.json`
- `release-decision.json`

Explain that the normalizer isolates the governance layer from the scanner-specific schema.

### 5. Show the policy

Open:

```text
policies/release-policy.toml