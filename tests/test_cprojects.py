import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperClassificationProject

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_cprojects(cprojects, expected_type=TrapperClassificationProject):
    """Common validation for deployments responses."""
    assert hasattr(cprojects, "results")
    assert hasattr(cprojects, "pagination")

    if cprojects.results:  # only if results is not empty
        assert isinstance(cprojects.results[0], expected_type)

#
# Classification Projects
#

def test_trapper_client_classification_projects_get_all(trapper_client):
    try:
        cp = trapper_client.classification_projects.get_all()
        _validate_cprojects(cp)
        logging.debug(f"Found {len(cp.results)} active cp.")
    except Exception as e:
        logging.debug(f"Error fetching cp: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_id(trapper_client):
    id_test = 33

    try:
        cp = trapper_client.classification_projects.get_by_id(id_test)
        _validate_cprojects(cp)
        assert cp.results[0].pk == id_test
        logging.debug(f"Found {len(cp.results)} active cp.")
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_classification_project_by_collection(trapper_client):
    id_test = 47

    try:
        cp = trapper_client.classification_projects.get_by_collection(id_test)
        _validate_cprojects(cp)
        #assert all(d.collection_pk==id_test for d in cp.results)
        logging.debug(f"Found {len(cp.results)} active cp.")
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"