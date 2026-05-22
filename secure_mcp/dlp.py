"""Very simple DLP-style scanner for the demo."""

SENSITIVE_PATTERNS = {
    "CONFIDENTIAL": "Confidential classification marker",
    "customer data": "Customer data reference",
    "internal strategy": "Internal strategy reference",
    "acquisition": "Acquisition-related information",
    "budget": "Budget information",
}


def scan_for_sensitive_data(text: str) -> dict:
    """Detect a small set of demo-sensitive markers."""
    findings = []
    lowered = text.lower()

    for pattern, description in SENSITIVE_PATTERNS.items():
        if pattern.lower() in lowered:
            findings.append(f"{pattern}: {description}")

    return {
        "contains_sensitive_data": bool(findings),
        "findings": findings,
    }
