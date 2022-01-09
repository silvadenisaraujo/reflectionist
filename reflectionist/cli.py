from pathlib import Path
from typing import Optional
import typer

from reflectionist import ERRORS, config, database, __version__, __app_name__
from reflectionist.service import Service

app = typer.Typer()


def get_service() -> Service:
    if config.CONFIG_FILE_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            'Config file not found. Please, run "reflectionist init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    if db_path.exists():
        return Service(db_path)
    else:
        typer.secho(
            'Database not found. Please, run "reflectionist init"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="reflections folder path",
    ),
) -> None:
    """Initialize the reflections database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The reflections database is {db_path}", fg=typer.colors.GREEN)


@app.command()
def create(
    happened: str = typer.Option(
        default=None, prompt="What happened that affected me?"
    ),
    felt: str = typer.Option(default=None, prompt="How did I feel then and now?"),
    learned: str = typer.Option(default=None, prompt="What did I learn about myself?"),
) -> None:
    """Create a new reflection."""
    service = get_service()
    _, return_code = service.add(happened=happened, felt=felt, learned=learned)
    if return_code != database.SUCCESS:
        typer.secho(
            f'Creating a reflection failed with "{ERRORS[return_code]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            "Reflection added!",
            fg=typer.colors.GREEN,
        )


@app.command()
def list() -> None:
    """List all reflections."""
    service = get_service()
    reflections = service.get()
    if len(reflections) == 0:
        typer.secho("There are no reflections yet", fg=typer.colors.RED)
        raise typer.Exit()
    typer.secho(f"{len(reflections)} reflections:", fg=typer.colors.BLUE)
    for i, reflection in enumerate(reflections):
        typer.secho(f"{i}. situation={reflection['happened']}", fg=typer.colors.BLUE)


@app.command()
def describe(id: int = typer.Option(default=None, prompt="Which reflection?")) -> None:
    """Describe a reflection given an id."""
    service = get_service()
    reflection = service.describe(id=id)
    typer.secho(reflection, fg=typer.colors.BLUE)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the app version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return


if __name__ == "__main__":
    app()
