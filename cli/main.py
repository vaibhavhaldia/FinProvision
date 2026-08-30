import typer
from cli.commands import scaffold

app = typer.Typer(
    name="tradeforge",
    help="TradeForge — Zero-touch. Banking-grade. 30 seconds.",
    no_args_is_help=True,
    add_completion=False,
)

app.add_typer(scaffold.app, name="scaffold")

if __name__ == "__main__":
    app()