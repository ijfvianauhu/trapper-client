import csv
import logging
from datetime import timezone

import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperDeployment
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

# Función común de validación de deployments
def _validate_deployments(deployments, expected_type=TrapperDeployment):
    """Common validation for deployments responses."""
    assert hasattr(deployments, "results")
    assert hasattr(deployments, "pagination")

    if deployments.results:  # solo si hay resultados
        assert isinstance(deployments.results[0], expected_type)

# Funciones de validación específicas
def validate_pk(results, expected):
    assert all(d.pk == expected for d in results)

def validate_owner(results, expected_owner):
    assert all(d.owner == expected_owner for d in results)

def validate_correct_setup(results, expected=True):
    assert all(d.correct_setup is expected for d in results)

def validate_correct_tstamp(results, expected=True):
    assert all(d.correct_tstamp is expected for d in results)

def validate_deployment_code(results, expected):
    assert all(d.deployment_code == expected for d in results)

def validate_deployment_id(results, expected):
    assert len(results) == 1
    assert all(d.deployment_id == expected for d in results)

def validate_location(results, expected):
    assert all(d.location == expected for d in results)

def validate_location_id(results, expected):
    assert all(d.location_id == expected for d in results)

def validate_research_project(results, expected):
    pass

def validate_sdate_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    expected_date = expected_date.replace(tzinfo=timezone.utc)
    assert all(d.start_date >= expected_date for d in results)

def validate_sdate_to(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    expected_date = expected_date.replace(tzinfo=timezone.utc)
    assert all(d.start_date <= expected_date for d in results)

def validate_edate_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    expected_date = expected_date.replace(tzinfo=timezone.utc)
    assert all(d.end_date >= expected_date for d in results)

def validate_edate_to(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    expected_date = expected_date.replace(tzinfo=timezone.utc)
    assert all(d.end_date <= expected_date for d in results)

def validate_classification_project(results, expected):
    pass

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "owner": validate_owner,
    "correct_setup": validate_correct_setup,
    "correct_tstamp": validate_correct_tstamp,
    "deployment_code": validate_deployment_code,
    "deployment_id": validate_deployment_id,
    "location": validate_location,
    "research_project": validate_research_project,
    "sdate_from": validate_sdate_from,
    "sdate_to": validate_sdate_to,
    "edate_from": validate_edate_from,
    "edate_to": validate_edate_to,
    "classification_project":validate_classification_project,
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 47),
        ("deployment_code", "R0001"),
        ("deployment_id", "r0001-wicp_0001"),
        ("owner", "trapper_client@uhu.es"),
        ("correct_setup", True),
        ("correct_tstamp", True),
        ("location", 213),
        ("research_project", [16]),
#        ("tags", [3, 4]),
        ("sdate_from", "2025-01-01"),
        ("sdate_to", "2025-12-31"),
        ("edate_from", "2025-01-01"),
        ("edate_to", "2025-12-31"),
        ("classification_project", 33),
    ]
)
def test_trapper_client_deployments_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "deployments", TrapperDeployment, VALIDATIONS)

def test_trapper_client_locations_get_by_id(trapper_client):
    id_test = 47
    try:
        locations = trapper_client.deployments.get_by_id(id_test)
        validate_objects(locations, TrapperDeployment)
        assert len(locations.results) == 1
        assert locations.results[0].pk == id_test
        logging.debug(f"Found {len(locations.results)} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_locations_export(trapper_client):
    expected_fields = [
    "deploymentID",
    "locationID",
    "locationName",
    "latitude",
    "longitude",
    "coordinateUncertainty",
    "deploymentStart",
    "deploymentEnd",
    "setupBy",
    "cameraID",
    "cameraModel",
    "cameraDelay",
    "cameraHeight",
    "cameraDepth",
    "cameraTilt",
    "cameraHeading",
    "detectionDistance",
    "timestampIssues",
    "baitUse",
    "featureType",
    "habitat",
    "deploymentGroups",
    "deploymentTags",
    "deploymentComments",
    "_id",
    ]

    try:
        response:csv.DictReader= trapper_client.deployments.export()
        assert isinstance(response, csv.DictReader)
        assert response.fieldnames == expected_fields
        logging.info(f"Found {response} active locations.")
    except Exception as e:
        logging.debug(f"Error fetching locations: {e}")
        assert False, f"Exception occurred: {e}"
