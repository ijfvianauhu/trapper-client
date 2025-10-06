import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperResearchProject

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_rprojects(cprojects, expected_type=TrapperResearchProject):
    """Common validation for deployments responses."""
    assert hasattr(cprojects, "results")
    assert hasattr(cprojects, "pagination")

    if cprojects.results:  # only if results is not empty
        assert isinstance(cprojects.results[0], expected_type)

#
# Deployments
#

def test_trapper_client_research_project_get_all(trapper_client):
    try:
        deployments = trapper_client.research_projects.get_all()
        _validate_rprojects(deployments)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_get_by_id(trapper_client):
    id_test = "16"
    try:
        deployments = trapper_client.research_projects.get_by_id(id_test)
        _validate_rprojects(deployments)
        assert len(deployments.results) == 1
        assert deployments.results[0].pk==int(id_test)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_acronym(trapper_client):
    acro_test = "WICP_01"

    try:
        deployments = trapper_client.research_projects.get_by_acronym(acro_test)
        _validate_rprojects(deployments)
        assert all(d.name==acro_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_owner(trapper_client):
    owner_test = "trapper_client@uhu.es"

    try:
        deployments = trapper_client.research_projects.get_by_owner(owner_test)
        _validate_rprojects(deployments)
        assert all(d.owner==owner_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_my(trapper_client):
    owner_test = "trapper_client@uhu.es"

    try:
        deployments = trapper_client.research_projects.get_my(owner_test)
        _validate_rprojects(deployments)
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
        _validate_rprojects(deployments)
        logging.debug(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"