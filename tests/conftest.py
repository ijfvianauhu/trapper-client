import os
import pytest
from trapper_client.TrapperClient import TrapperClient
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture(scope="module")
def trapper_client():
    load_dotenv()
    client = TrapperClient.from_environment()
    assert client.base_url.startswith("http")
    return client

@pytest.fixture
def existing_subjectset_name():
    return os.getenv("TEST_EXISTING_SUBJECTSET_NAME")

@pytest.fixture
def existing_subjectset_id():
    return int(os.getenv("TEST_EXISTING_SUBJECTSET_ID"))