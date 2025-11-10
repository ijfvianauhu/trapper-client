from pathlib import Path
from typing import Annotated

import typer
from typer_config import use_yaml_config
import logging
import gettext, yaml
from trapper_client.ui.typer.commands import locations, deployments, classification_projects, research_projects, collections, resources, media, observations
#, research_projects, classification_projects, collections, resources, media, observations)
from trapper_client.ui.typer.TyperUtils import TyperUtils
from trapper_client.TrapperClient import TrapperClient

from rich.console import Console
from rich.table import Table

console = Console()
TyperUtils.console = console
logger = logging.getLogger(__name__)
_ = gettext.gettext

APP_NAME="trapper-client-ui"

app = typer.Typer(help=_("CLI for testing TrapperClient"), rich_markup_mode='markdown')

# Registrar subcomandos
app.add_typer(locations.app, name="locations")
app.add_typer(deployments.app, name="deployments")
app.add_typer(research_projects.app, name="research-projects")
app.add_typer(classification_projects.app, name="classification-projects")
app.add_typer(collections.app, name="collections")
app.add_typer(resources.app, name="resources")
app.add_typer(media.app, name="media")
app.add_typer(observations.app, name="observations")

def get_default_config_file() -> Path:
    """Obtiene la ruta al fichero de configuración por defecto."""
    app_dir = Path(typer.get_app_dir(APP_NAME))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / "config.yaml"

def ensure_config_file() -> Path:
    """Crea el fichero de configuración con valores por defecto si no existe
    y asegura que el fichero de log también exista."""
    config_file = get_default_config_file()

    if not config_file.exists():
        default_config = {
            "login": {
                "username": "myuser",
                "password": "mypassword",
                "trapper_url": "https://wildintel-trap.uhu.es",
                "token": "",
            },
            "logger": {
                "lang": "en",
                "loglevel": "INFO",
                "logfilename": str(config_file.parent / "app.log"),
            },
        }

        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

    # Asegurarse de que el fichero de log exista
    with open(yaml.safe_load(open(config_file))["logger"]["logfilename"], "a") as f:
        pass

    return config_file

def init_logger(logfilename: Path, loglevel:str, lang:str):
    """Inicializa el logger y la configuración de i18n."""
    global logger, _

    logging.basicConfig(
        level=loglevel.upper(),
        filename=logfilename,
        filemode="a",
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    logger = logging.getLogger(__name__)

    # Configuración de i18n
    locale_dir = Path(__file__).parent / "locales"

    try:
        translation = gettext.translation(
            "messages", localedir=locale_dir, languages=[lang]
        )
        _ = translation.gettext
    except FileNotFoundError as e:
        print(e)
        _ = gettext.gettext

@app.callback()
@use_yaml_config(default_value=ensure_config_file())
def common_setup(
        ctx: typer.Context,
        logfilename: Annotated[Path, typer.Option()] = None,
        loglevel: Annotated[str, typer.Option()] = None,
        lang: Annotated[str, typer.Option()] = None,
        username: Annotated[str, typer.Option()] = None,
        password: Annotated[str, typer.Option()] = None,
        trapper_url: Annotated[str, typer.Option()] = None,
        token: Annotated[str, typer.Option()] = None,
):
    # Cargar config YAML entera
    import yaml
    config_file = ensure_config_file()
    with open(config_file) as f:
        config = yaml.safe_load(f)

    logger_cfg = config.get("logger", {})
    login_cfg = config.get("login", {})

    # Usar CLI > YAML > defaults
    logfilename = logfilename or Path(logger_cfg.get("logfilename", "app.log"))
    loglevel = loglevel or logger_cfg.get("loglevel", "INFO")
    lang = lang or logger_cfg.get("lang", "en")

    username = username or login_cfg.get("username")
    password = password or login_cfg.get("password")
    trapper_url = trapper_url or login_cfg.get("trapper_url")
    token = token or login_cfg.get("token")

    trapper_client=TrapperClient(
        access_token= token if token else None,
        base_url=trapper_url,
        user_name=username if username else None,
        user_password=password if password else None,
    )

    # Inicializa logger
    init_logger(logfilename, loglevel, lang)

    ctx.obj = {
        "logger": logging.getLogger(__name__),
        "_": _,
       "trapper_client": trapper_client
    }

@app.command("show-logger", help=_("Show log file content"), short_help=_("Show log file content"))
def show_logger():

    config_file = ensure_config_file()
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)  # Devuelve un diccionario de Python

    log_path = Path(config.get("logger", {}).get("logfilename", "app.log"))

    if log_path.exists():
        with log_path.open("r") as f:
            content = f.read()
        print(content)
    else:
        TyperUtils.fatal(_(f"Log file not found: {log_path}"))

@app.command("show-config", help=_("Show current configuration"), short_help=_("Show current configuration"))
def show_config():
    config_file = ensure_config_file()
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)  # Devuelve un diccionario de Python

    table = Table(title=_("Configuration"))
    table.add_column(_("Section"), style="cyan")
    table.add_column(_("Key"), style="green")
    table.add_column(_("Value"), style="magenta")

    for section, values in config.items():
        if isinstance(values, dict):
            for key, value in values.items():
                table.add_row(section, key, str(value))
        else:
            # Para claves de nivel superior que no pertenezcan a ninguna sección
            table.add_row("None", section, str(values))

    console.print(table)

@app.command("set-config", help=_("Set a configuration parameter"), short_help=_("Set a configuration parameter"))
def set_config(key: str, value: str):
    """Modifica un parámetro Archivos procesados conde la configuración"""
    config_file = ensure_config_file()

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    found = False
    for section, values in config.items():
        if isinstance(values, dict) and key in values:
            values[key] = value
            found = True
            break

    if not found:
        TyperUtils.fatal(_(f"'{key}' is not a valid parameter"))

    # Guardar la configuración YAML actualizada
    with open(config_file, "w") as f:
        yaml.dump(config, f, sort_keys=False)

    TyperUtils.success(_(f"Configuration updated in {config_file}"))


if __name__ == "__main__":
    app()
