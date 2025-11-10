import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperCollection, TrapperCollectionRP, TrapperCollectionCP
from .helpers import run_test_by_filters, validate_objects

#
# pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

# Funciones de validación específicas
def validate_pk(results, expected):
    assert all(d.pk == expected for d in results)

def validate_keywords(results, expected):
    pass

def validate_acronym(results, expected):
    assert all(d.name == expected for d in results)

    assert all(d.name == expected for d in results)

def validate_status(results, expected):
    assert all(d.status == expected for d in results)

def validate_owners(results, expected):
    mapping = {10:"trapper_client@uhu.es"}
    assert all(d.owner == mapping.get(expected, "") for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "keywords": validate_keywords,
    "name": validate_acronym,
    "status": validate_status,
    "owners": validate_owners
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 25   ),
        ("name", "WICP_01"),
#        ("keywords", "WICP"),
        ("status","Private"),
        ("owners",10)
    ]

#"owner",  # OwnCollectionBooleanFilter
#"research_projects",
#"locations_map",
)

def test_trapper_client_collection_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "collections", TrapperCollection, VALIDATIONS)

def test_trapper_client_collections_get_all(trapper_client):
    try:
        rps = trapper_client.collections.get_all()
        validate_objects(rps, TrapperCollection)
        logging.info(f"Found {len(rps.results)} active research project.")
    except Exception as e:
        logging.debug(f"Error fetching research project: {e}")
        assert False, f"Exception occurred: {e}"


def test_trapper_client_collections_get_by_id(trapper_client):
    id_test = "25"
    try:
        collections = trapper_client.collections.get_by_id(id_test)
        validate_objects(collections, TrapperCollection)
        assert len(collections.results) == 1
        assert collections.results[0].pk==int(id_test)
        logging.debug(f"Found {len(collections.results)} active collections whose id is {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_research_project(trapper_client):
    id_test = "16"
    try:
        collections = trapper_client.collections.get_by_research_project(id_test)
        validate_objects(collections, expected_type=TrapperCollectionRP)
        logging.debug(f"Found {len(collections.results)} active collections for rproject {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_collections_get_by_classification_project(trapper_client):
    id_test = "33"
    try:
        collections = trapper_client.collections.get_by_classification_project(id_test)
        validate_objects(collections, expected_type=TrapperCollectionCP)
        logging.debug(f"Found {len(collections.results)} active collections for cproject {id_test}.")
        #print(f"Found {len(resources.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching collections: {e}")
        assert False, f"Exception occurred: {e}"