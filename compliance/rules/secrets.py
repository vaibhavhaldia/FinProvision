"""Secrets detection rules."""
from typing import NamedTuple

class Rule(NamedTuple):
    pattern: str
    severity: str
    rule_id: str
    description: str

SECRET_RULES: list[Rule] = [
    Rule(r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']', "CRITICAL", "TF-SEC-001", "Hardcoded password"),
    Rule(r'(?i)(api_key|apikey|api[-_]key)\s*[=:]\s*["\'][^"\']{10,}["\']', "CRITICAL", "TF-SEC-002", "Hardcoded API key"),
    Rule(r'AKIA[0-9A-Z]{16}', "CRITICAL", "TF-SEC-003", "AWS Access Key ID exposed"),
    Rule(r'(?i)bearer\s+[a-zA-Z0-9_\-]{20,}', "CRITICAL", "TF-SEC-004", "Hardcoded Bearer token"),
    Rule(r'(?i)(secret|token)\s*[=:]\s*["\'][^"\']{8,}["\']', "HIGH", "TF-SEC-005", "Hardcoded secret/token"),
    Rule(r'dapi[a-zA-Z0-9]{32}', "CRITICAL", "TF-SEC-006", "Databricks personal access token"),
    Rule(r'(?i)(private_key|rsa_key)\s*[=:]\s*["\']-----BEGIN', "CRITICAL", "TF-SEC-007", "Private key material in code"),
    Rule(r'ghp_[a-zA-Z0-9]{36}', "CRITICAL", "TF-SEC-008", "GitHub personal access token"),
]