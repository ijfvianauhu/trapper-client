import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperMedia

#
#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_media(media, expected_type=TrapperMedia):
    """Common validation for deployments responses."""
    assert hasattr(media, "results")
    assert hasattr(media, "pagination")

    if media.results:  # only if results is not empty
        assert isinstance(media.results[0], expected_type)

def test_trapper_client_media_get_all(trapper_client):
    try:
        deployments = trapper_client.media.get_all()
        assert False, "Not implemented yet"
    except NotImplementedError as e:
        assert True, f"Exception occurred: {e}"
    except Exception as e:
        print(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_media_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        media = trapper_client.media.get_by_classification_project(id_test)
        _validate_media(media)
        logging.debug(f"Found {len(media.results)} active media in classification project {id_test}.")
    except Exception as e:
        logging.debug(f"Exception occurred: {e}")
        assert False, f"Exception occurred: {e}"