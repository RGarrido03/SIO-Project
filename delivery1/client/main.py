import typer

from commands import anonymous

app = typer.Typer(name="SIO Project - Client")
app.add_typer(anonymous.app)

if __name__ == "__main__":
    app()
