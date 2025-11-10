import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperResearchProject
from .helpers import run_test_by_filters, validate_objects

#
# pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

# Funciones de validación específicas
def validate_pk(results, expected):
    assert all(d.pk == expected for d in results)

def validate_keywords(results, expected):
    pass

def validate_acronym(results, expected):
    assert all(d.acronym == expected for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "keywords": validate_keywords,
    "acronym": validate_acronym,
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 16),
        ("acronym", "WICP_01"),
#        ("keywords", "WICP"),
    ]
)
def test_trapper_client_rproject_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "research_projects", TrapperResearchProject, VALIDATIONS)

def test_trapper_client_research_project_get_all(trapper_client):
    try:
        rps = trapper_client.research_projects.get_all()
        validate_objects(rps,TrapperResearchProject)
        logging.info(f"Found {len(rps.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_owner(trapper_client):
    owner_test = "trapper_client@uhu.es"

    try:
        deployments = trapper_client.research_projects.get_by_owner(owner_test)
        validate_objects(deployments,TrapperResearchProject)
        assert all(d.owner==owner_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_owners(trapper_client):
    owner_test = ["trapper_client@uhu.es",]

    try:
        deployments = trapper_client.research_projects.get_by_owners(owner_test)
        validate_objects(deployments,TrapperResearchProject)
        assert all(d.owner in owner_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_my(trapper_client):
    owner_test = "trapper_client@uhu.es"

    try:
        deployments = trapper_client.research_projects.get_my(owner_test)
        validate_objects(deployments, TrapperResearchProject)
        assert all(
            (proj.owner == owner_test) or any(
                role.username == owner_test and any(r in ["Admin", "Collaborator", "Expert"] for r in role.roles)
                for role in proj.project_roles or []
            )
            for proj in deployments.results
        )
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_collection(trapper_client):
    collection_test = "15"

    try:
        deployments = trapper_client.research_projects.get_by_collection(collection_test)
        validate_objects(deployments, TrapperResearchProject)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"