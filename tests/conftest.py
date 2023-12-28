# -*- coding: utf-8 -*-

import requests
import pytest


from bookops_bpl_solr import SolrSession


class MockUnexpectedException:
    def __init__(self, *args, **kwargs):
        raise Exception


class MockTimeout:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.Timeout


class MockConnectionError:
    def __init__(self, *args, **kwargs):
        raise requests.exceptions.ConnectionError


class MockSuccessfulHTTP200SessionResponse:
    def __init__(self):
        self.status_code = 200


@pytest.fixture
def mock_unexpected_error(monkeypatch):
    monkeypatch.setattr("requests.Session.get", MockUnexpectedException)


@pytest.fixture
def mock_timeout(monkeypatch):
    monkeypatch.setattr("requests.Session.get", MockTimeout)


@pytest.fixture
def mock_connectionerror(monkeypatch):
    monkeypatch.setattr("requests.Session.get", MockConnectionError)


@pytest.fixture
def mock_successful_session_get_response(monkeypatch):
    def mock_api_response(*args, **kwargs):
        return MockSuccessfulHTTP200SessionResponse()

    monkeypatch.setattr(requests.Session, "get", mock_api_response)


@pytest.fixture
def default_payload():
    return {
        "rows": 10,
        "fq": "ss_type:catalog",
    }


@pytest.fixture
def stub_session():
    with SolrSession(authorization="my_client_key", endpoint="url_here") as session:
        return session


@pytest.fixture
def live_key():
    """
    runs only locally ; since the service have IP restrictions it most likely
    won't run on Travis
    """
    import os
    import json
    from collections import namedtuple

    if os.name == "nt":
        Cred = namedtuple("Cred", ["endpoint", "client_key"])
        fh = os.path.join(os.environ["USERPROFILE"], ".cred/.solr/bpl-solr-prod.json")
        with open(fh, "r") as file:
            cred = json.load(file)
            return Cred(cred["endpoint"], cred["client_key"])
