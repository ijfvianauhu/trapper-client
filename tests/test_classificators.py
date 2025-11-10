import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from .helpers import run_test_by_filters, validate_objects, validate_pk, validate_name
from trapper_client.Schemas import TrapperClassificator

#
# pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client


def validate_resource_type(results, expected):
    assert all(d.resource_type == expected for d in results)


def validate_status(results, expected):
    pass

def validate_rdata_from(results, expected):
    from datetime import datetime
    expected_date = datetime.fromisoformat(expected)
    assert all(d.date_recorded >= expected_date for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "name": validate_name,
    "status": validate_status,
    "rdate_from": validate_rdata_from
}


# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value",
    [
        ("pk", 1   ),
        ("name", "Zooniverse Donana"),
#explicit_fields = [
#"name",
#"owner",
#"template",  # inline, upload, etc.
#"species",  # all species
#"tracked_species",
#"observation_type",
#"is_setup",
#"sex",
#"age",
#"count",
#"count_new",
#"behaviour",
#"individual_id",
#"classification_confidence",
#"updated_date",
#]

    ]
)
def test_trapper_client_classificator_filters(trapper_client, filter_name, filter_value):
    run_test_by_filters(trapper_client, filter_name, filter_value, "classificators", TrapperClassificator, VALIDATIONS)

def test_trapper_client_classificator_get_all(trapper_client):
    try:
        resources = trapper_client.classificators.get_all()
        validate_objects(resources, expected_type=TrapperClassificator)
        logging.debug(f"Found {len(resources.results)} active resources.")
    except Exception as e:
        print(f"Error fetching resources: {e}")
        assert False, f"Exception occurred: {e}"


def _test_trapper_client_classificator_get_by_owner(trapper_client):
    name =  "trapper_client@uhu.es"
    try:
        classificators = trapper_client.classificators.get_by_owner(query={"owner":name})
        _validate_classificators(classificators, expected_type=TrapperClassificator)
        assert all(c.owner == name for c in classificators.results)
        logging.info(f"Found {len(classificators.results)} active classificators.")
    except Exception as e:
        logging.debug(f"Error fetching classificators: {e}")
        assert False, f"Exception occurred: {e}"
