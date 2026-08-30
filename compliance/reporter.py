"""Reporter — formats findings as text or SARIF."""
from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING
from rich.console import Console
from rich.table import Table
from rich import box
if TYPE_CHECKING:
    from compliance.scanner import Finding

SEVERITY_COLOR = {"CRITICAL": "red bold", "HIGH": "yellow", "MEDIUM": "cyan", "LOW": "dim"}
SARIF_LEVEL = {"CRITICAL": "error", "HIGH": "warning", "MEDIUM": "note", "LOW": "none"}

class Reporter:
    def __init__(self, findings: list["Finding"]) -> None:
        self.findings = findings

    def print_text(self, console: Console) -> None:
        if not self.findings:
            console.print("\n[green bold]✓ 0 violations — compliance gate passed.[/green bold]")
            return
        by_severity: dict[str, list] = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}
        for f in self.findings:
            by_severity.setdefault(f.severity, []).append(f)
        table = Table(
            title=f"Compliance Scan — {len(self.findings)} finding(s)",
            box=box.ROUNDED,
            border_style="red" if by_severity["CRITICAL"] else "yellow",
            show_header=True, header_style="bold",
        )
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Rule ID", width=12)
        table.add_column("Description", width=40)
        table.add_column("File", width=30)
        table.add_column("Line", justify="right", width=6)
        for severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            for f in by_severity.get(severity, []):
                color = SEVERITY_COLOR.get(severity, "")
                table.add_row(f"[{color}]{severity}[/{color}]", f.rule_id, f.description,
                    f.file_path[-28:] if len(f.file_path) > 28 else f.file_path, str(f.line_number))
        console.print(table)

    def write_sarif(self, output_path: Path) -> None:
        rules, results, seen = [], [], set()
        for f in self.findings:
            if f.rule_id not in seen:
                rules.append({"id": f.rule_id, "name": f.description.replace(" ", ""),
                    "shortDescription": {"text": f.description},
                    "defaultConfiguration": {"level": SARIF_LEVEL.get(f.severity, "note")}})
                seen.add(f.rule_id)
            results.append({"ruleId": f.rule_id, "level": SARIF_LEVEL.get(f.severity, "note"),
                "message": {"text": f"{f.description} [{f.severity}]"},
                "locations": [{"physicalLocation": {"artifactLocation": {"uri": f.file_path},
                    "region": {"startLine": f.line_number}}}]})
        sarif = {"$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0", "runs": [{"tool": {"driver": {"name": "TradeForge Compliance Scanner",
            "version": "0.1.0", "rules": rules}}, "results": results}]}
        output_path.write_text(json.dumps(sarif, indent=2))