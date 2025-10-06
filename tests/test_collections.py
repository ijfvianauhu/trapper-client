import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperCollection, TrapperCollectionCP, TrapperCollectionRP

#
#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def _validate_collections(collections, expected_type=TrapperCollection):
    """Common validation for deployments responses."""
    assert hasattr(collections, "results")
    assert hasattr(collections, "pagination")

    if collections.results:  # only if results is not empty
        assert isinstance(collections.results[0], expected_type)

def test_trapper_client_collections_get_all(trapper_client):
    try:
        collections = trapper_client.collections.get_all()
        _validate_collections(collections)
        #TrapperClient.export_list_to_csv(collections, "/tmp/collections_all.csv")
        logging.debug(f"Found {len(collections.results)} active collections.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_id(trapper_client):
    id_test = "25"
    try:
        collections = trapper_client.collections.get_by_id(id_test)
        _validate_collections(collections)
        assert len(collections.results) == 1
        assert collections.results[0].pk==int(id_test)
        logging.debug(f"Found {len(collections.results)} active collections whose id is {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_acronym(trapper_client):
    id_test = "R0001"
    try:
        collections = trapper_client.collections.get_by_acronym(id_test)
        _validate_collections(collections)
        assert all(d.name==id_test for d in collections.results)
        logging.debug(f"Found {len(collections.results)} active collections whose name it {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_research_project(trapper_client):
    id_test = "16"
    try:
        collections = trapper_client.collections.get_by_research_project(id_test)
        _validate_collections(collections, expected_type=TrapperCollectionRP)
        logging.debug(f"Found {len(collections.results)} active collections for rproject {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        collections = trapper_client.collections.get_by_classification_project(id_test)
        _validate_collections(collections, expected_type=TrapperCollectionCP)
        logging.debug(f"Found {len(collections.results)} active collections for cproject {id_test}.")
        #print(f"Found {len(resources.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"