"""ComplianceScanner — regex rule engine."""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from compliance.rules.secrets import SECRET_RULES, Rule
from compliance.rules.pii import PII_RULES
from compliance.rules.banking import BANKING_RULES

SCAN_EXTENSIONS = {".py", ".ts", ".js", ".yaml", ".yml", ".json", ".tf", ".hcl", ".sh", ".env", ".txt"}
SKIP_PATTERNS = {".venv", "node_modules", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "compliance-report.sarif", "compliance/rules/"}
ALL_RULES: list[Rule] = SECRET_RULES + PII_RULES + BANKING_RULES

@dataclass
class Finding:
    rule_id: str
    severity: str
    description: str
    file_path: str
    line_number: int
    line_content: str

class ComplianceScanner:
    def __init__(self, rules: list[Rule] | None = None) -> None:
        self.rules = rules or ALL_RULES
        self._compiled = [(re.compile(rule.pattern), rule) for rule in self.rules]

    def scan(self, path: Path) -> list[Finding]:
        findings: list[Finding] = []
        if path.is_file():
            findings.extend(self._scan_file(path))
        elif path.is_dir():
            for file_path in self._walk(path):
                findings.extend(self._scan_file(file_path))
        return findings

    def _walk(self, root: Path) -> Iterator[Path]:
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix not in SCAN_EXTENSIONS:
                continue
            path_str = str(p)
            if any(skip in path_str for skip in SKIP_PATTERNS):
                continue
            yield p

    def _scan_file(self, file_path: Path) -> list[Finding]:
        findings: list[Finding] = []
        try:
            content = file_path.read_text(errors="replace")
        except (OSError, PermissionError):
            return findings
        lines = content.splitlines()
        for line_no, line in enumerate(lines, start=1):
            for compiled_pattern, rule in self._compiled:
                if compiled_pattern.search(line):
                    findings.append(Finding(
                        rule_id=rule.rule_id, severity=rule.severity,
                        description=rule.description, file_path=str(file_path),
                        line_number=line_no, line_content=line,
                    ))
        return findings