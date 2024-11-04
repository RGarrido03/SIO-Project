import typer

from commands import anonymous

app = typer.Typer()
app.add_typer(anonymous.app)

if __name__ == "__main__":
    app()
