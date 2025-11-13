import logging
import pytest
from dotenv import load_dotenv
from trapper_client.TrapperClient import TrapperClient
from trapper_client.Schemas import TrapperResearchProject
from .helpers import run_test_by_filters, validate_objects

logger = logging.getLogger(__name__)

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
    assert all(d.acronym == expected for d in results)


def test_trapper_client_packages_generate(trapper_client):
    cp=33
    a=trapper_client.packages.generate(cp=cp, params={"filter_deployments": "DEPLOYMENT", "clear_cache": True})
    logger.info(a)
    assert a.get("errors") is None

def test_trapper_client_packages_download(trapper_client):
    cp=33
    a=trapper_client.packages.generate(cp=cp)
    package = a.get("package", None)

    a=trapper_client.packages.download(package_url=package, destination_folder="/tmp")

    logger.info(a)