import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperObservation

#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_observations(observations, expected_type=TrapperObservation):
    """Common validation for deployments responses."""
    assert hasattr(observations, "results")
    assert hasattr(observations, "pagination")

    if observations.results:  # only if results is not empty
        assert isinstance(observations.results[0], expected_type)

def test_trapper_client_observations_get_all(trapper_client):
    try:
        deployments = trapper_client.observations.get_all()
        assert False, "Not implemented yet"
    except NotImplementedError as e:
        assert True, f"Exception occurred: {e}"
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_observations_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        resources = trapper_client.observations.get_by_classification_project(id_test)
        _validate_observations(resources)
        logging.debug(f"Found {len(resources.results)} active observations in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"