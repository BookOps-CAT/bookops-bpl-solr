# -*- coding: utf-8 -*-

"""
Tests session.py module
"""

import pytest

from bookops_bpl_solr.session import SolrSession, BplSolrError
from bookops_bpl_solr import __title__, __version__


class TestSolrSession:
    """
    Tests SolrSession class
    """

    def test_init_authorization_param(self):
        session = SolrSession("my_client_key", "example.com")
        assert session.authorization == "my_client_key"

    @pytest.mark.parametrize("arg", [None, "", 123])
    def test_init_argument_authorization_exception(self, arg):
        err_msg = "Invalid authorization. Argument must be a Client-Key string."
        with pytest.raises(BplSolrError) as exc:
            SolrSession(authorization=arg, base_url="example.com")
            assert err_msg in str(exc.value)

    def test_init_base_url_param(self):
        session = SolrSession("my_client_key", "example.com")
        assert session.base_url == "example.com"

    @pytest.mark.parametrize("arg", [None, "", 123])
    def test_init_argument_base_url_exceptions(self, arg):
        err_msg = "Invalid base_url argument. It must be a Client-Key string."
        with pytest.raises(BplSolrError) as exc:
            SolrSession(authorization="my_client_key", base_url=arg)
            assert err_msg in str(exc.value)

    @pytest.mark.parametrize("arg", [None, "", [], {}])
    def test_init_agent_default_param(self, arg):
        session = SolrSession("my_client_key", "example.com", agent=arg)
        assert session.agent == f"{__title__}/{__version__}"

    def test_init_agent_custom_param(self):
        session = SolrSession("my_client_key", "example.com", agent="my_client")
        assert session.agent == "my_client"

    @pytest.mark.parametrize("arg", [123, {"a": 1}])
    def test_init_agent_argument_exceptions(self, arg):
        err_msg = "Invalid type of an agent argument."
        with pytest.raises(BplSolrError) as exc:
            SolrSession("my_client_key", "example.com", agent=arg)
            assert err_msg in str(exc.value)
