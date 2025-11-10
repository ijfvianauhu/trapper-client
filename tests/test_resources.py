import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperResource, TrapperResourceLocation
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

def validate_resource_type(results, expected):
    assert all(d.resource_type == expected for d in results)

def validate_name(results, expected):
    assert all(d.name == expected for d in results)

def validate_status(results, expected):
    pass

def validate_rdata_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    assert all(d.date_recorded >= expected_date for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "resource_type": validate_resource_type,
    "name": validate_name,
    "status": validate_status,
    "rdate_from": validate_rdata_from
}

#explicit_fields = [
#    "rdate_from",  # BaseDateFilter sobre date_recorded__date (gte)
#    "rdate_to",  # BaseDateFilter sobre date_recorded__date (lte)
#    "udate_from",  # BaseDateFilter sobre date_uploaded__date (gte)
#    "udate_to",  # BaseDateFilter sobre date_uploaded__date (lte)
#    "rtime_from",  # BaseTimeFilter sobre date_recorded (gte)
#    "rtime_to",  # BaseTimeFilter sobre date_recorded (lte)
#    "owner",  # OwnResourceBooleanFilter
#    "locations_map",  # BaseLocationsMapFilter sobre deployment__location
#    "collections",  # MultipleChoiceFilter
#    "deployments",  # CharFilter, método get_deployments
#    "deployment__isnull",  # BooleanFilter
#    "tags",  # MultipleChoiceFilter
#    "observation_type",  # CharFilter, método get_observation_type
#    "species",  # CharFilter, método get_species
#    "timestamp_error",  # BooleanFilter, método get_timestamp_error
#]

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 1   ),
        ("name", "IMG_1998"),
        ("resource_type", "I"),
        ("status","Private"),
        ("rdate_from", "2025-05-02"),
    ]

#"owner",  # OwnCollectionBooleanFilter
#"research_projects",
#"locations_map",
)
def test_trapper_client_resource_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "resources", TrapperResource, VALIDATIONS)

def test_trapper_client_resources_get_all(trapper_client):
    try:
        resources = trapper_client.resources.get_all()
        validate_objects(resources, expected_type=TrapperResource)
        logging.debug(f"Found {len(resources.results)} active resources.")
    except Exception as e:
        print(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_resources_get_by_collection(trapper_client):
    id_test = "47"
    try:
        resources = trapper_client.resources.get_by_collection(id_test)
        validate_objects(resources, expected_type=TrapperResource)
        logging.debug(f"Found {len(resources.results)} active resources in collection {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_resources_get_by_location(trapper_client):
    id_test = "213"
    try:
        resources = trapper_client.resources.get_by_location(id_test)
        validate_objects(resources, expected_type=TrapperResourceLocation)
        logging.debug(f"Found {len(resources.results)} active resources in location {id_test}.")
    except Exception as e:
        logging.debug(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"