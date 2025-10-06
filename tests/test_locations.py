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
# Locations
#

def test_trapper_client_locations_get_all(trapper_client):

    try:
        locations = trapper_client.locations.get_all()
        assert hasattr(locations, "results")
        assert hasattr(locations, "pagination")
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_id(trapper_client):
    id_test = "216"
    try:
        locations = trapper_client.locations.get_by_id(id_test)
        assert hasattr(locations, "results")
        assert hasattr(locations, "pagination")
        assert len(locations.results) == 1
        assert locations.results[0].id == id_test
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_acronym(trapper_client):
    acro_test = "wicp_0002"
    try:
        locations = trapper_client.locations.get_by_acronym(acro_test)
        assert hasattr(locations, "results")
        assert hasattr(locations, "pagination")
        assert len(locations.results) == 1
        assert locations.results[0].locationID == acro_test
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_rs(trapper_client):
    acro_test = "16.0"
    count_expected = 3
    try:
        locations = trapper_client.locations.get_by_research_project(acro_test)
        assert hasattr(locations, "results")
        assert hasattr(locations, "pagination")
        assert len(locations.results) == count_expected
    except Exception as e:
        print(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"
