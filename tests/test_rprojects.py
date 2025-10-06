#from typer.testing import CliRunner

import pytest
from trapper_client.TrapperClient import TrapperClient
from dotenv import load_dotenv
#runner = CliRunner()

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

#
# Deployments
#

def test_trapper_client_research_project_get_all(trapper_client):
    try:
        deployments = trapper_client.research_projects.get_all()
        assert hasattr(deployments, "results")
        print(f"Found {len(deployments.results)} active research project.")
    except Exception as e:
        print(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_get_by_id(trapper_client):
    id_test = "16"
    try:
        deployments = trapper_client.research_projects.get_by_id(id_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == 1
        assert deployments.results[0].pk==int(id_test)
        print(f"Found {len(deployments.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_acronym(trapper_client):
    acro_test = "WICP_01"

    try:
        deployments = trapper_client.research_projects.get_by_acronym(acro_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == 1
        assert deployments.results[0].name==acro_test
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_owner(trapper_client):
    owner_test = "trapper_client@uhu.es"
    count_expected = 2

    try:
        deployments = trapper_client.research_projects.get_by_owner(owner_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == count_expected
        assert deployments.results[0].owner==owner_test
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_my(trapper_client):
    owner_test = "trapper_client@uhu.es"
    count_expected = 2

    try:
        deployments = trapper_client.research_projects.get_my(owner_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == count_expected
        assert deployments.results[0].owner==owner_test
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_research_project_by_collection(trapper_client):
    collection_test = "trapper_client@uhu.es"
    count_expected = 2

    try:
        deployments = trapper_client.research_projects.get_by_collection(collection_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == count_expected
        assert deployments.results[0].owner==collection_test
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"