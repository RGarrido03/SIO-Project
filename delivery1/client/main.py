import typer

from commands import anonymous, authenticated, local, authorized

app = typer.Typer(name="SIO Project - Client")
app.registered_commands.extend(anonymous.app.registered_commands)
app.registered_commands.extend(authenticated.app.registered_commands)
app.registered_commands.extend(local.app.registered_commands)
app.registered_commands.extend(authorized.app.registered_commands)

if __name__ == "__main__":
    app()
