import typer

from commands import anonymous

app = typer.Typer(name="SIO Project - Client")
app.registered_commands.extend(anonymous.app.registered_commands)


if __name__ == "__main__":
    app()
