import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperObservationResults, TrapperClassification, TrapperUserClassification, \
    TrapperAIClassification, ClassificationResultsAgg, TrapperAIObservationResultsTrapper, \
    TrapperAIObservationResultsCTDP

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
    for d in results:
        logging.info(len(d.dynamic_attrs))
    assert all(d.resource.deployment == expected for d in results)

def validate_approved(results, expected):
    expected_bool = expected.lower() == "true"
    assert all(d.approved == expected_bool for d in results)

def validate_observation_type(results, expected):
    for r in results:
        attributes = getattr(r, 'dynamic_attrs', None)
        assert all( atr.observation_type == expected for atr in attributes)

# Diccionario de validaciones por filtro
VALIDATIONS = {
    "pk": validate_pk,
    "deployment": validate_deployment,
    "approved": validate_approved,
    "observation_type": validate_observation_type,
#    "keywords": validate_keywords,
#    "name": validate_acronym,
#    "status": validate_status,
#    "owners": validate_owners
}

# Parametrización de filtros a testear
@pytest.mark.parametrize(
    "filter_name,filter_value,query",
    [
        #"pk"
        #"project",
        #"deployment",
        # ("deployment", 898, {"project":"33"}),
        #"collection",
        #"ftype",
        #"species",
        #"observation_type",
        #"bboxes",
        #"approved",
        #"confidence",
        #"ai_provider",

        #("pk", 16372, {}),
        #("project", 33, {}),
        #("approved", "false", {"project":"33"}),
        #("observation_type", "human", {})
    ]
)
def test_trapper_client_aiobservationsresults_filters(trapper_client, filter_name, filter_value,query):
    run_test_by_filters(trapper_client, filter_name, filter_value,
                        "aiobservations.results",
                        TrapperAIClassification,
                        VALIDATIONS,
                        query)

def test_trapper_client_aiobservations_results_get_all_camtrap(trapper_client):
    cp_id = 33
    query = {"camtrapdp": "True"}

    try:
        trapper_client.aiobservations.results.set_camtrapdp_format()
        observations = trapper_client.aiobservations.results.get_all(cp_id, query=query)
        logging.debug(observations)
        validate_objects(observations, expected_type=TrapperAIObservationResultsCTDP)
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

def test_trapper_client_aiobservations_results_get_deployment_camtrap(trapper_client):
    cp_id = 33
    query = {"camtrapdp": "True", "deployment": 898, "project":cp_id}

    try:
        observations = trapper_client.aiobservations.results.get_all(cp_id, query=query)
        logging.info(observations.results[0])
        validate_objects(observations, expected_type=TrapperAIObservationResultsCTDP)
        assert all(o.deploymentID == 'r9999-dona_0036' for o in observations.results)
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"


def test_trapper_client_aiobservations_results_get_all_nocamtrap(trapper_client):
    cp_id = 33
    query = {"camtrapdp": "False"}

    try:
        observations = trapper_client.aiobservations.results.get_all(cp_id, query=query)
        logging.debug(observations)
        validate_objects(observations, expected_type=TrapperAIObservationResultsTrapper)
        logging.info(f"Found {len(observations.results)} active observations.")
    except Exception as e:
        logging.debug(f"Error fetching observations: {e}")
        assert False, f"Exception occurred: {e}"

