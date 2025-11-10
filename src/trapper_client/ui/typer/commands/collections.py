import typer, logging,gettext
from trapper_client.TrapperClient import TrapperClient
from trapper_client.ui.typer.TyperUtils import TyperUtils

app = typer.Typer(help="Manage Collections")

logger = logging.getLogger(__name__)
_ = gettext.gettext

@app.command("all",
    short_help=_("Retrieve all collections based on optional query parameters"),
    help=_("This command allows users to fetch collections from the database. Query parameters can be provided to filter results, and the output can optionally be exported to a CSV file.")
)
def get_all(
        ctx: typer.Context,
        query: str = typer.Option(None, help="Query parameters as key=value,key=value"),
        export: str = typer.Option(None, help="Export results to CSV file")) -> None:
    """
    Retrieve all collections based on optional query parameters.

    This command allows users to fetch collections from the database.
    Query parameters can be provided to filter results, and the output can
    optionally be exported to a CSV file.

    Args:
        ctx (typer.Context): The Typer context object, used to share information across commands.
        query (str, optional): Query parameters in the format `key=value,key=value` to filter projects.
        export (str, optional): Path to a CSV file where the results will be exported.

    Returns:
        None: Prints the collections  details to the CLI output or to csv file.

    """

    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    query_dict = dict(item.split("=") for item in query.split(",")) if query else None
    results = trapper_client.collections.get_all(query=query_dict)
    logger.info(f"Retrieved {len(results.results)} collections")
    logger.debug(results.model_dump_json(indent=4) )

    if export:
        trapper_client.export_list_to_csv(results, output_file=export)
    else:
        TyperUtils.json2Table(results, title="Collections")

@app.command("id",
    short_help=_("Retrieve a specific collection by its unique ID."),
    help=_("This command fetches detailed information about a single collection, based on the provided collection ID.")
)
def get_by_id(
        ctx: typer.Context,
        rp_id: str = typer.Argument(..., help=_("The unique ID of the classification to fetch"))
) -> None:
    """
    Retrieve a specific collection by its unique ID.

    This command fetches detailed information about a collection, based on the provided collection ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        rp_id (str): The unique identifier of the collection to retrieve.

    Returns:
        None: Prints the collection details to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.collections.get_by_id(rp_id)
    if len(result.results) > 0:
        TyperUtils.print_pydantic_card(result.results[0], title=f"Collection {rp_id}")

@app.command("acronym",
    short_help=_("Retrieve collections based on their acronym."),
    help=_("This command fetches detailed information about collections using the provided acronym to identify it.")
)
def get_by_acronym(
    ctx: typer.Context,
    acronym: str = typer.Argument(..., help=_("The acronym of the research project we are interested in"))
) -> None:
    """
    Retrieve collections based on their acronym.

    This command fetches detailed information about collections using the provided acronym to identify it.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        acronym (str): The acronym of the collections of interest.

    Returns:
        None: Prints the collections details to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.collections.get_by_acronym(acronym)
    TyperUtils.json2Table(result, title=f"Collections with acronym {acronym}")

@app.command("classification-project",
    short_help=_("Retrieve all collections associated with a specific classification project."),
    help=_("This command fetches collections that belong to a classification project by its unique collection ID.")
)
def get_by_classification_project(
    ctx: typer.Context,
    cproject_id: str = typer.Argument(..., help=_("The unique ID of the classification project whose collections will be fetched"))
) -> None:
    """
    Retrieve all collections associated with a specific classification project.

    This command fetches collections that belong to a classification project identified
    by its unique project ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        cproject_id(str): The unique ID of the classification project whose collections will be retrieved.

    Returns:
        None: Prints the list of collections to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.collections.get_by_classification_project(cproject_id)
    TyperUtils.json2Table(result, title=f"Collections used in classification project {cproject_id}")

@app.command("research-project",
    short_help=_("Retrieve all collections associated with a specific research project."),
    help=_("This command fetches collections that belong to a research project identified by its unique ID.")
)
def get_by_research_project(
    ctx: typer.Context,
    rproject_id: str = typer.Argument(..., help=_("The unique ID of the research project whose collections will be fetched"))
) -> None:
    """
    Retrieve all collections associated with a specific research project.

    This command fetches collections that belong to a research project identified
    by its unique ID.

    Args:
        ctx (typer.Context): The Typer context object, used for managing
            CLI state and parameters.
        rproject_id(str): The unique ID of the research project whose collections will be retrieved.

    Returns:
        None: Prints the list of collections to the CLI output.
    """
    logger = ctx.obj["logger"]
    _ = ctx.obj["_"]
    trapper_client = ctx.obj["trapper_client"]

    result = trapper_client.collections.get_by_research_project(rproject_id)
    TyperUtils.json2Table(result, title=f"Collections used in classification project {rproject_id}")

