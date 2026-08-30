import typer
from pathlib import Path
from config import load_config

app = typer.Typer(help="Run individual TradeForge generators.")


@app.callback(invoke_without_command=True)
def scaffold(
    type: str = typer.Option(..., "--type", "-t"),
    config: Path = typer.Option("service.yaml", "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    sarif:  str = typer.Option(None, "--sarif", help="Write SARIF report to this path"),
) -> None:
    spec = load_config(str(config))

    if type == "terraform":
        from generators.terraform_gen import TerraformGenerator

        TerraformGenerator(spec, dry_run=dry_run).generate()

    elif type == "actions":
        from generators.github_actions_gen import GitHubActionsGenerator

        GitHubActionsGenerator(spec, dry_run=dry_run).generate()

    elif type == "notebooks":
        from generators.databricks_gen import DatabricksGenerator

        DatabricksGenerator(spec, dry_run=dry_run).generate()
        
    elif type == "atlassian":
        from generators.atlassian_gen import run_atlassian
        run_atlassian(spec)

    elif type == "compliance":
        from compliance.scanner import ComplianceScanner
        from compliance.reporter import Reporter
        from rich.console import Console
        import sys
        console = Console()
        target = Path(config).parent   # scan the project root
        
        console.print(f"[cyan]Scanning {target} for compliance violations...[/cyan]")
        scanner = ComplianceScanner()
        findings = scanner.scan(target)
        
        reporter = Reporter(findings)
        reporter.print_text(console)
        
        if sarif:
            reporter.write_sarif(Path(sarif))
            console.print(f"[dim]SARIF report written to {sarif}[/dim]")
        
        critical_count = sum(1 for f in findings if f.severity == "CRITICAL")
        if critical_count > 0:
            console.print(f"\n[red bold]✗ Compliance gate FAILED — {critical_count} CRITICAL finding(s)[/red bold]")
            sys.exit(1)
        else:
            console.print(f"\n[green bold]✓ Compliance gate PASSED[/green bold]")

    else:
        print(f"Unknown type: {type}")
        raise typer.Exit(1)
