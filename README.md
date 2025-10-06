# trapper-client
Python wrapper for [Trapper API]("https://gitlab.com/trapper-projec")
This work is heavily inspired by the Python wrapper for Zoom API [Zoomus](https://github.com/prschmid/zoomus)

## Installation

```
git clone https://github.com/ijfvianauhu/trapper-client
cd trapper-client
poetry install
```

## Configuration

## Usage

### Create TrapperClient instance

TrapperClient supports two authentication methods against Trapper:

* Token-based authentication (using an API token)
* User/password authentication (using a username and password)

By default, TrapperClient will try to authenticate with a token.  If no token is provided, it will automatically fall 
back to username and password authentication.

To create a TrapperClient instance using username and password:

```python
from trapper_client.TrapperClient import TrapperClient

trapper_client = TrapperClient(
    trapper_url="https://trapper.example.org",
    trapper_user="my_user",
    trapper_password="my_password"
)
```
But if you want to use token-based authentication, you can do it like this:

```python
trapper_client = TrapperClient(
    trapper_url="https://trapper.example.org",
    trapper_token="my_user",
)
```

Also, TrapperClient can be initialized by using environment variables. If we want to use environment variables, we can
do the following:

```python
from trapper_client.TrapperClient import TrapperClient

trapper_client = TrapperClient.from_environment()
```
This code assumes the following environment variables are defined:

* TRAPPER_URL
* TRAPPER_USER
* TRAPPER_PASSWORD
* TRAPPER_ACCESS_TOKEN

### Locations

Fetch all locations from the API

```python
from trapper_client.TrapperClient import TrapperClient

trapper_client = TrapperClient.from_environment()
locations = trapper_client.locations.get_all()
```

Fetch a location by its ID

```python
from trapper_client.TrapperClient import TrapperClient
id_test = "216"
trapper_client = TrapperClient.from_environment()
locations = trapper_client.locations.get_id(id_test)
```

Fetch a location by its acronym

```python
from trapper_client.TrapperClient import TrapperClient
acro_test = "wicp_0002"
trapper_client = TrapperClient.from_environment()
locations = trapper_client.locations.get_by_acronym(acro_test)   
```

Fetch locations by research project ID

```python
from trapper_client.TrapperClient import TrapperClient
id_test = "16.0"
trapper_client = TrapperClient.from_environment()
locations = trapper_client.locations.get_by_research_project(id_test)   
```