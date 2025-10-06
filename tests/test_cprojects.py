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
# Classification Projects
#

def test_trapper_client_classification_projects_get_All(trapper_client):
    try:
        cp = trapper_client.classification_projects.get_all()
        assert hasattr(cp, "results")
        print(f"Found {len(cp.results)} active cp.")
    except Exception as e:
        print(f"Error fetching cp: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_id(trapper_client):
    id_test = 12222

    try:
        cp = trapper_client.classification_projects.get_by_id(id_test)
        assert hasattr(cp, "results")
        assert len(cp.results) == 1
        assert cp.results[0].pk == id_test
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"