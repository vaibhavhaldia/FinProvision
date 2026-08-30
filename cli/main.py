import typer
from cli.commands.scaffold import app as scaffold_app
from cli.commands.init import init

app = typer.Typer()
app.add_typer(scaffold_app, name="scaffold")
app.command("init")(init)

if __name__ == "__main__":
    app()