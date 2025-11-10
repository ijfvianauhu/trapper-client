import csv
import logging
import pytest
from dotenv import load_dotenv

from tests.helpers import run_test_by_filters
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperLocation

#
# pytest -v -o log_cli=true --log-cli-level=DEBUG
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

def validate_resource_type(results, expected):
    assert all(d.resource_type == expected for d in results)

def validate_name(results, expected):
    assert all(d.name == expected for d in results)

def validate_location_id(results, expected):
    assert len(results) == 1
    assert all(d.location_id == expected for d in results)

def validate_owner(results, expected):
    assert all(d.owner == "trapper_client@uhu.es" for d in results)

def validate_owners(results, expected):
    mapping = {10:"trapper_client@uhu.es"}
    assert all(d.owner == mapping.get(expected, "") for d in results)

def validate_description(results, expected):
    assert all(d.description == expected for d in results)

def validate_research_project(results, expected):
    mapping = {16:"WICP_01"}
    assert all(d.research_project == mapping.get(expected,"") for d in results)

def validate_deployments(results, expected):
    pass

def validate_is_public(results, expected):
    bool_expected = expected.lower() == "true"
    assert all(d.is_public == bool_expected for d in results)

def log_validate_locations_map(results, expected):
    pass

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "name": validate_name,
    "location_id": validate_location_id,
    "description": validate_description,
    "owner": validate_owner,
    "owners" : validate_owners,
    "research_project" : validate_research_project,
    "deployments" : validate_deployments,
    "is_public" : validate_is_public,
#"city",
#"country",
#"state",
#"county"
#    "locations_map" : validate_locations_map,
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 216),
        ("name", "WICP_0002"),
        ("location_id", "dona_0036"),
        ("description", "none"),
        ("owner", "true"),
        ("owners", 10),
        ("research_project", 16),
        ("deployments", 47),
        ("locations_map", 5),
        ("is_public", "true"),
    ]
#"city",
#"country",
#"state",
#"county"
#    "locations_map" : validate_locations_map,
)
def test_trapper_client_locations_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "locations", TrapperLocation, VALIDATIONS)

def test_trapper_client_locations_get_all(trapper_client):

    try:
        locations = trapper_client.locations.get_all()
        validate_objects(locations, TrapperLocation)
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_id(trapper_client):
    id_test = 216
    try:
        locations = trapper_client.locations.get_by_id(id_test)
        validate_objects(locations, TrapperLocation)
        assert len(locations.results) == 1
        assert locations.results[0].pk == id_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def _test_trapper_client_locations_get_by_name(trapper_client):
    name_test = "WICP_0002"
    try:
        locations = trapper_client.locations.get_by_name(name_test)
        validate_objects(locations, TrapperLocation)
        assert len(locations.results) == 1
        assert locations.results[0].name == name_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_get_by_acro(trapper_client):
    acro_test = "dona_0036"
    try:
        locations = trapper_client.locations.get_by_acronym(acro_test)
        validate_objects(locations, TrapperLocation)
        assert len(locations.results) == 1
        assert locations.results[0].location_id == acro_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_export(trapper_client):
    expected_fields = [
        'locationID',
        'longitude',
        'latitude',
        'country',
        'timezone',
        'ignoreDST',
        'habitat',
        'comments',
        '_id',
        'researchProject'
    ]
    try:
        response:csv.DictReader= trapper_client.locations.export()
        #_validate_objects(response)
        assert isinstance(response, csv.DictReader)
        assert response.fieldnames == expected_fields
        logging.info(f"Found {response} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"
