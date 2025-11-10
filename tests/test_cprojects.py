import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import  TrapperClassificationProject
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

def validate_pk(results, expected):
    assert (len(results) == 1)
    assert all(d.pk == expected for d in results)

def validate_owner(results, expected):
    pass

def validate_research_project(results, expected):
    map = { 16 : "WICP_01"}
    assert all(d.research_project == map.get(expected,"") for d in results)

def validate_status(results, expected):
    map = { 1 : "Ongoing"}
    assert all(d.status == map.get(expected,"") for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "owner": validate_owner,
    "research_project": validate_research_project,
    "status": validate_status
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 35),
        ("owner", True),
        ("research_project",16),
        ("status",  1)
    ]
)

def test_trapper_client_classification_projects_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "classification_projects", TrapperClassificationProject, VALIDATIONS)

#
# Classification Projects
#

def test_trapper_client_classification_projects_get_all(trapper_client):
    try:
        cp = trapper_client.classification_projects.get_all()
        validate_objects(cp, TrapperClassificationProject)
        logging.info(f"Found {len(cp.results)} active cp.")
        logging.info(cp.results)
    except Exception as e:
        logging.debug(f"Error fetching cp: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_name(trapper_client):
    id_test = "WICP_01_CP_ZOO"

    try:
        cp = trapper_client.classification_projects.get_by_name(id_test)
        validate_objects(cp, TrapperClassificationProject)
        assert all(d.name == id_test for d in cp.results)
        logging.info(f"Found {len(cp.results)} active cp named {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_owners(trapper_client):
    owners = ("trapper_client@uhu.es",)

    try:
        cp = trapper_client.classification_projects.get_by_owners(owners)
        validate_objects(cp, TrapperClassificationProject)
        assert all(d.owner in owners for d in cp.results)
        logging.info(f"Found {len(cp.results)} active cp for owner {owners}.")
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_collection(trapper_client):
    id_test = 47

    try:
        cp = trapper_client.classification_projects.get_by_collection(id_test)
        validate_objects(cp, TrapperClassificationProject)
        #assert all(d.collection_pk==id_test for d in cp.results)
        logging.debug(f"Found {len(cp.results)} active cp.")
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"