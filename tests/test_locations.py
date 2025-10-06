import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperLocation

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_locations(locations, expected_type=TrapperLocation):
    """Common validation for deployments responses."""
    assert hasattr(locations, "results")
    assert hasattr(locations, "pagination")

    if locations.results:  # only if results is not empty
        assert isinstance(locations.results[0], expected_type)

#
# Locations
#

def test_trapper_client_locations_get_all(trapper_client):

    try:
        locations = trapper_client.locations.get_all()
        _validate_locations(locations)
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_id(trapper_client):
    id_test = "216"
    try:
        locations = trapper_client.locations.get_by_id(id_test)
        _validate_locations(locations)
        assert len(locations.results) == 1
        assert locations.results[0].id == id_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_acronym(trapper_client):
    acro_test = "wicp_0002"
    try:
        locations = trapper_client.locations.get_by_acronym(acro_test)
        _validate_locations(locations)
        assert len(locations.results) == 1
        assert locations.results[0].locationID == acro_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_rp(trapper_client):
    id_test = "16.0"
    try:
        locations = trapper_client.locations.get_by_research_project(id_test)
        _validate_locations(locations)
        assert all(d.researchProject==id_test for d in locations.results)
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"