import typer
from pathlib import Path
from config import load_config

app = typer.Typer(help="Run individual TradeForge generators.")


@app.callback(invoke_without_command=True)
def scaffold(
    type: str = typer.Option(..., "--type", "-t"),
    config: Path = typer.Option("service.yaml", "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run"),
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

    else:
        print(f"Unknown type: {type}")
        raise typer.Exit(1)
