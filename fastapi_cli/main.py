import typer
from .model_generator import make_model
from .controller_generator import make_controller

app = typer.Typer()

app.command()(make_model)
app.command()(make_controller)

@app.command("make:all")
def make_all(name: str):
    """
    Create both model and controller files.
    """
    typer.echo(f"Creating model and controller for {name}")
    make_model(name)
    make_controller(f"{name}Controller", model_name=name)

if __name__ == "__main__":
    app()
    