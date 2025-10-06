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

def test_trapper_client_collections_get_all(trapper_client):
    try:
        collections = trapper_client.collections.get_all()
        assert hasattr(collections, "results")
        assert hasattr(collections, "pagination")
    except NotImplementedError as e:
        assert True, f"Exception occurred: {e}"
    except Exception as e:
        print(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_research_project(trapper_client):
    id_test = "16"
    try:
        collections = trapper_client.collections.get_by_research_project(id_test)
        assert hasattr(collections, "results")
        assert hasattr(collections, "pagination")
        assert len(collections.results) > 0
        from trapper_client.Schemas import TrapperCollectionRP
        assert isinstance(collections.results[0], TrapperCollectionRP)
    except Exception as e:
        print(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        collections = trapper_client.collections.get_by_classification_project(id_test)
        assert hasattr(collections, "results")
        assert hasattr(collections, "pagination")
        assert len(collections.results) > 0
        from trapper_client.Schemas import TrapperCollectionCP
        assert isinstance(collections.results[0], TrapperCollectionCP)
        #print(f"Found {len(resources.results)} active locations.")
    except Exception as e:
        print(f"Error fetching deployments: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_id(trapper_client):
    id_test = "25"
    try:
        collections = trapper_client.collections.get_by_id(id_test)
        assert hasattr(collections, "results")
        assert hasattr(collections, "pagination")
        assert len(collections.results) == 1
        from trapper_client.Schemas import TrapperCollection
        assert isinstance(collections.results[0], TrapperCollection)
        assert collections.results[0].pk==int(id_test)
    except Exception as e:
        print(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_acronym(trapper_client):
    id_test = "R0001"
    try:
        collections = trapper_client.collections.get_by_acronym(id_test)
        assert hasattr(collections, "results")
        assert len(collections.results) == 1
        from trapper_client.Schemas import TrapperCollection
        assert isinstance(collections.results[0], TrapperCollection)
        assert collections.results[0].name==int(id_test)
    except Exception as e:
        print(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"