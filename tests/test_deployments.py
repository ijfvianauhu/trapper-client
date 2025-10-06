import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperDeployment

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_deployments(deployments, expected_type=TrapperDeployment):
    """Common validation for deployments responses."""
    assert hasattr(deployments, "results")
    assert hasattr(deployments, "pagination")

    if deployments.results:  # only if results is not empty
        assert isinstance(deployments.results[0], expected_type)

#
# Deployments
#

def test_trapper_client_deployments_get_all(trapper_client):
    try:
        deployments = trapper_client.deployments.get_all()
        _validate_deployments(deployments)
        logging.debug(f"Found {len(deployments.results)} active deployments.")
    except Exception as e:
        logging.debug(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_deployments_get_by_id(trapper_client):
    id_test = "46"
    try:
        deployments = trapper_client.deployments.get_by_id(id_test)
        _validate_deployments(deployments)
        assert len(deployments.results) == 1
        assert deployments.results[0].id==id_test
        logging.debug(f"Found {len(deployments.results)} active deployments.")
    except Exception as e:
        logging.debug(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_deployments_by_acronym(trapper_client):
    acro_test = "dd-wicp_0001"

    try:
        deployments = trapper_client.deployments.get_by_acronym(acro_test)
        _validate_deployments(deployments)
        assert all(d.deploymentID == acro_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active deployments.")
    except Exception as e:
        logging.debug(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_deployments_by_location(trapper_client):
    id_test = "wicp_0001"
    try:
        deployments = trapper_client.deployments.get_by_location(id_test)
        _validate_deployments(deployments)
        assert all(d.locationID==id_test for d in deployments.results)
        logging.debug(f"Found {len(deployments.results)} active deployments.")
    except Exception as e:
        logging.debug(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"