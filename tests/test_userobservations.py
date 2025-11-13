import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperObservationResults, TrapperClassification, TrapperUserClassification, \
    TrapperAIClassification, ClassificationResultsAgg

from .helpers import validate_objects, run_test_by_filters


#  pytest -o log_cli=true --log-cli-level=DEBUG
#

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

def validate_pk(results, expected):
    assert len(results) == 1
    assert all(d.pk == expected for d in results)

def validate_deployment(results, expected):
    assert all(d.resource.deployment == expected for d in results)

def validate_approved(results, expected):
    expected_bool = expected.lower() == "true"
    assert all(d.approved == expected_bool for d in results)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "deployment": validate_deployment,
    "approved": validate_approved,
#    "keywords": validate_keywords,
#    "name": validate_acronym,
#    "status": validate_status,
#    "owners": validate_owners
}

"""explicit_fields = [
    "pk",
    "project",
    "user",
    "owner",
    "deployment",
    "collection",
    "species",
    "ftype",
    "approved",
    "bboxes",
    "feedback",
    "observation_type",
    "locations_map",
    "rdate_from",
    "rdate_to",
    "rtime_from",
    "rtime_to"
]"""
# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value,query",
    [
        ("pk", 16372, {}),
        ("project", 33, {}),
        ("deployment", 898, {"project":"33"}),
        ("approved", "false", {"project":"33"}),
#        ("name", "WICP_01"),
#        ("keywords", "WICP"),
#        ("status","Private"),
#        ("owners",10)
    ]
)
def _test_trapper_client_userobservations_filters(trapper_client, filter_name, filter_value,query):
    run_test_by_filters(trapper_client, filter_name, filter_value,
                        "userobservations",
                        TrapperAIClassification,
                        VALIDATIONS,
                        query)


def test_trapper_client_observations_get_by_collections(trapper_client):
    cp_id = 33
    c_id = 47

    try:
        observations = trapper_client.userobservations.get_by_collection(cp_id,c_id)
        logging.info(observations)
        validate_objects(observations, expected_type=TrapperUserClassification)

        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_observations_get_all(trapper_client):
    try:
        observations = trapper_client.userobservations.get_all()
        validate_objects(observations, expected_type=TrapperUserClassification)
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"
