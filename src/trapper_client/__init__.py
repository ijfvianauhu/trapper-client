"""
Trapper Client
==============

The **Trapper Client** is a lightweight Python interface for interacting with the
[`Trapper`](https://gitlab.com/trapper-project/trapper/) API — a platform for managing, processing, and classifying
camera trap data within research and conservation projects.

This client provides a unified, programmatic way to interact with multiple API endpoints,
including **classification projects**, **collections**, **media resources**, and more.

It handles authentication, pagination, and object mapping into **Pydantic models**, so
users can interact with the API using clean Python objects instead of raw JSON.

---

Main Components
---------------

The package is organized into modular components, each responsible for a specific
set of API endpoints:

- ``trapper_client.components.ResearchProjectComponent``
    Manage and query ResearchProject data associated with media resources.

- ``trapper_client.components.LocationsComponent``
    Manage and query location data associated with media resources.

- ``trapper_client.components.DeploymentsComponent`
    Manage and query deployments data associated with media resources.

- ``trapper_client.components.CollectionsComponent``
  Access and manage image collections linked to classification projects.

- ``trapper_client.components.ClassificationProjectsComponent``
  Manage and query classification projects.

- ``trapper_client.components.MediaComponent``
  Handle media resources such as images and videos, supporting advanced filters
  (e.g., by collection, species, or date).

- ``trapper_client.Schemas``
  Pydantic models used to serialize and validate API responses.

- ``trapper_client.TrapperAPIClient``
  Main entry point for authentication and session handling.

---

Example
-------

The following example shows how to authenticate and retrieve classification projects
using the client:

.. code-block:: python

    from trapper_client import TrapperAPIClient

    # Create and authenticate the client
    client = TrapperAPIClient(
        base_url="https://wildintel-trap.uhu.es",
        username="your_username",
        password="your_password"
    )

    # Access the classification projects component
    projects = client.classification_projects.get_all()

    # Print project names
    for p in projects.results:
        print(p.name)

---

Configuration
-------------

The client can be configured using environment variables or YAML configuration files.
Typical configuration keys include:

- ``trapper_url`` – Base URL of the API
- ``trapper_user`` – Username for authentication
- ``trapper_password`` – User password
- ``trapper_token`` – authentication token (if applicable)

---

:copyright:
    © 2025 WildINTEL / Universidad de Huelva
:license:
    MIT License
"""

__version__ = "0.1.0"
