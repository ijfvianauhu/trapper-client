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

def test_trapper_client_deployments_get_all(trapper_client):
    try:
        deployments = trapper_client.deployments.get_all()
        assert hasattr(deployments, "results")
        print(f"Found {len(deployments.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_deployments_get_by_id(trapper_client):
    id_test = "46"
    try:
        deployments = trapper_client.deployments.get_by_id(id_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == 1
        assert deployments.results[0].id==id_test
        print(f"Found {len(deployments.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_deployments_by_acronym(trapper_client):
    acro_test = "dd-wicp_0001"

    try:
        deployments = trapper_client.deployments.get_by_acronym(acro_test)
        assert hasattr(deployments, "results")
        assert len(deployments.results) == 1
        assert deployments.results[0].deploymentID==acro_test
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"
