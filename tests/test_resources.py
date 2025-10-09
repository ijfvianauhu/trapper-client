import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperResource, TrapperResourceCollection, TrapperResourceLocation

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_resources(resources, expected_type=TrapperResource):
    """Common validation for deployments responses."""
    assert hasattr(resources, "results")
    assert hasattr(resources, "pagination")

    if resources.results:  # only if results is not empty
        assert isinstance(resources.results[0], expected_type)

#
# Deployments
#

def _test_trapper_client_resources_get_all(trapper_client):
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
        _validate_resources(resources, expected_type=TrapperResourceCollection)
        logging.debug(f"Found {len(resources.results)} active resources in collection {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_resources_get_by_location(trapper_client):
    id_test = "213"
    try:
        resources = trapper_client.resources.get_by_location(id_test)
        _validate_resources(resources, expected_type=TrapperResourceLocation)
        logging.debug(f"Found {len(resources.results)} active resources in location {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"