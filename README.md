# <img src="img/wildIntel_logo.webp" alt="Trapper Client Logo" height="60">  trapper-client

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-GPLv3-blue.svg)
[![WildINTEL](https://img.shields.io/badge/WildINTEL-v1.0-blue)](https://wildintel.eu/)
[![Trapper](https://img.shields.io/badge/Trapper-Server-green)](https://gitlab.com/trapper-project/trapper)

<hr>

## Python wrapper for [Trapper API]("https://gitlab.com/trapper-projec"). This work is heavily inspired by the Python wrapper for Zoom API [Zoomus](https://github.com/prschmid/zoomus)

## 🚀 Features

- **Collections Information**: Retrieve detailed information about Trapper collections
- **Classification Projects**: Access and manage Zooniverse classification projects
- **Deployments**: Obtain deployment-related data from Trapper
- **Locations**: Get geographic and contextual information about camera trap locations
- **Resources**: Retrieve metadata and media resources linked to collections
- **Observations**: Access processed wildlife observations and related data
- **Classification Media**: Manage and obtain media associated with classification projects

## 🧭 Overview

**Trapper-Zooniverse** is a Python wrapper for the **Trapper API**, designed to simplify access to data related to wildlife 
monitoring projects.  

This library provides convenient methods to interact with Trapper endpoints and retrieve structured information about 
collections, deployments, locations, resources, and observations, as well as classification projects and their 
associated media.  

This work is heavily inspired by the Python wrapper for the **Zoom API — [Zoomus](https://github.com/prschmid/zoomus)**, 
following a similar design philosophy of clean, intuitive access to API endpoints.

## 💻 Installation

Clone this repository and move into its directory:

```
git clone https://github.com/ijfvianauhu/trapper-client
cd trapper-client
poetry install
```

Create a virtual environment, its dependencies and compile translation files:

```python
poetry install
poetry run compile-mo
```

Now you can run all commands within this isolated environment.
```
poetry shell
```

## ⚙️ Configuration

## ⚡ Usage

Once you’ve installed [Trapper-Zooniverse](https://github.com/ijfvianauhu/trapper-client), you can start using it 
right away from the command line. Here’s what a typical first session looks like from a user’s perspective 

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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the GNU General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.


## 🏛️ Funding

This work is part of the [WildINTEL project](https://wildintel.eu/), funded by the Biodiversa+ Joint Research Call 2022-2023 “Improved
transnational monitoring of biodiversity and ecosystem change for science and society (BiodivMon)”. Biodiversa+ is the 
European co-funded biodiversity partnership supporting excellent research on biodiversity with an impact for policy and
society. Biodiversa+ is part of the European Biodiversity Strategy for 2030 that aims to put Europe’s biodiversity on a
path to recovery by 2030 and is co-funded by the European Commission. 