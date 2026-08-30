"""tradeforge init — runs all generators in sequence."""
from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from config import load_config

init_app = typer.Typer(help="Initialise a new service — runs all generators.")


# @init_app.command()
def init(
    config: str = typer.Option(..., "--config", help="Path to service.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would run, skip all API calls"),
    sarif: str = typer.Option(None, "--sarif", help="Write SARIF compliance report to this path"),
):
    console = Console()
    spec = load_config(Path(config))

    console.print(f"\n[bold cyan]TradeForge Init — {spec.service.name}[/bold cyan]")
    console.print(f"[dim]Domain: {spec.service.domain} | Env: {spec.service.env}[/dim]\n")

    if dry_run:
        console.print("[yellow bold]DRY RUN — no files written, no API calls made[/yellow bold]\n")
        _print_dry_run_plan(spec, console)
        return

    steps = [
        ("Compliance scan", _run_compliance),
        ("Terraform", _run_terraform),
        ("GitHub Actions", _run_actions),
        ("Databricks notebooks", _run_databricks),
        ("Atlassian (Jira + Confluence ADR)", _run_atlassian),
    ]

    failed = False
    for label, fn in steps:
        console.rule(f"[bold]{label}[/bold]")
        try:
            fn(spec, console, sarif=sarif if label == "Compliance scan" else None)
        except SystemExit:
            console.print(f"\n[red bold]✗ Init ABORTED — compliance gate failed[/red bold]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ {label} failed: {e}[/red]")
            failed = True

    if failed:
        console.print("\n[yellow bold]⚠ Init completed with warnings[/yellow bold]")
    else:
        console.print("\n[green bold]✓ Init complete — all generators ran successfully[/green bold]")


def _run_compliance(spec, console: Console, sarif: str | None = None) -> None:
    from compliance.scanner import ComplianceScanner
    from compliance.reporter import Reporter

    target = Path(".").resolve()
    scanner = ComplianceScanner()
    findings = scanner.scan(target)
    reporter = Reporter(findings)
    reporter.print_text(console)

    if sarif:
        reporter.write_sarif(Path(sarif))
        console.print(f"[dim]SARIF written to {sarif}[/dim]")

    critical_count = sum(1 for f in findings if f.severity == "CRITICAL")
    if critical_count > 0:
        console.print(f"[red bold]✗ {critical_count} CRITICAL finding(s) — aborting init[/red bold]")
        sys.exit(1)


def _run_terraform(spec, console: Console, **_) -> None:
    from generators.terraform_gen import TerraformGenerator
    gen = TerraformGenerator(spec)
    output_dir = gen.generate()
    console.print(f"[green]✓ Terraform written to {output_dir}[/green]")


def _run_actions(spec, console: Console, **_) -> None:
    from generators.github_actions_gen import GitHubActionsGenerator
    gen = GitHubActionsGenerator(spec)
    output_path = gen.generate()
    console.print(f"[green]✓ GitHub Actions written to {output_path}[/green]")


def _run_databricks(spec, console: Console, **_) -> None:
    from generators.databricks_gen import DatabricksGenerator
    gen = DatabricksGenerator(spec)
    paths = gen.generate()
    for p in paths:
        console.print(f"[green]✓ Notebook: {p}[/green]")


def _run_atlassian(spec, console: Console, **_) -> None:
    from generators.atlassian_gen import run_atlassian
    run_atlassian(spec)


def _print_dry_run_plan(spec, console: Console) -> None:
    console.print("[dim]Would run the following generators:[/dim]\n")
    steps = [
        ("Compliance scan", "Scan project root for secrets, PII, banking violations"),
        ("Terraform", f"Generate VPC + S3 + IAM for {spec.service.name}"),
        ("GitHub Actions", f"Generate CI/CD pipeline → .github/workflows/{spec.service.name}.yml"),
        ("Databricks", f"Generate ingestion notebook(s) for domain: {spec.service.domain}"),
        ("Atlassian", f"Create Jira epic '{spec.atlassian.epic_name if spec.atlassian else 'N/A'}' + stories + Confluence ADR"),
    ]
    for label, description in steps:
        console.print(f"  [cyan]•[/cyan] [bold]{label}[/bold] — {description}")
    console.print()
