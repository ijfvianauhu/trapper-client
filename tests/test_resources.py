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

def test_trapper_client_resources_get_all(trapper_client):
    try:
        deployments = trapper_client.resources.get_all()
        assert False, "Not implemented yet"
    except NotImplementedError as e:
        assert True, f"Exception occurred: {e}"
    except Exception as e:
        print(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_resources_get_by_collection(trapper_client):
    id_test = "47"
    try:
        resources = trapper_client.resources.get_by_collection(id_test)
        assert hasattr(resources, "results")
        assert len(resources.results) > 0
        #assert resources.results[0].pk==int(id_test)
        #print(f"Found {len(resources.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_resources_get_by_location(trapper_client):
    id_test = "213"
    try:
        resources = trapper_client.resources.get_by_location(id_test)
        assert hasattr(resources, "results")
        assert len(resources.results) > 0
        #assert resources.results[0].pk==int(id_test)
        print(f"Found {len(resources.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"