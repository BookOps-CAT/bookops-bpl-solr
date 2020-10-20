# -*- coding: utf-8 -*-

"""
Tests session.py module
"""

import pytest

from bookops_bpl_solr.session import SolrSession, BookopsSolrError
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
        with pytest.raises(BookopsSolrError) as exc:
            SolrSession(authorization=arg, endpoint="example.com")
            assert err_msg in str(exc.value)

    def test_init_endpoint_param(self):
        session = SolrSession("my_client_key", "example.com")
        assert session.endpoint == "example.com"

    @pytest.mark.parametrize("arg", [None, "", 123])
    def test_init_argument_endpoint_exceptions(self, arg):
        err_msg = "Invalid endpoint argument. It must be a Client-Key string."
        with pytest.raises(BookopsSolrError) as exc:
            SolrSession(authorization="my_client_key", endpoint=arg)
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
        with pytest.raises(BookopsSolrError) as exc:
            SolrSession("my_client_key", "example.com", agent=arg)
            assert err_msg in str(exc.value)

    def test_authorization_in_header(self):
        session = SolrSession("my_client_key", "example.com")
        assert session.headers["Client-Key"] == "my_client_key"

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            (
                {},
                {
                    "rows": 10,
                    "fq": "ss_type:catalog",
                },
            ),
            (
                {"rows": 10, "q": "isbn:isbn_here", "fl": "id,title,author_raw"},
                {
                    "q": "isbn:isbn_here",
                    "rows": 10,
                    "fq": "ss_type:catalog",
                    "fl": "id,title,author_raw",
                },
            ),
        ],
    )
    def test_merge_payload_with_defaults(self, arg, expectation):
        session = SolrSession("my_client_key", "example.com")
        assert session._merge_with_payload_defaults(arg) == expectation

    @pytest.mark.parametrize("arg", [({}, None, "some_str")])
    def test_send_request_payload_errors(self, arg):
        err_msg = "Missing or invalid payload argument."
        session = SolrSession("my_client_key", "example.com")
        with pytest.raises(BookopsSolrError) as exc:
            session._send_request(arg)
            assert err_msg in str(exc.value)

    def test_send_request_success(self, mock_successful_session_get_response):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            response = session._send_request({"q": "zendegi"})
            assert response.status_code == 200

    def test_send_request_timeout_error(self, mock_timeout):
        with pytest.raises(BookopsSolrError):
            with SolrSession(
                authorization="my_client_key", endpoint="example.com"
            ) as session:
                session._send_request({"q": "zendegi"})

    def test_send_request_connection_error(self, mock_connectionerror):
        with pytest.raises(BookopsSolrError):
            with SolrSession(
                authorization="my_client_key", endpoint="example.com"
            ) as session:
                session._send_request({"q": "zendegi"})

    def test_send_request_unexpected_error(self, mock_unexpected_error):
        with pytest.raises(BookopsSolrError):
            with SolrSession(
                authorization="my_client_key", endpoint="example.com"
            ) as session:
                session._send_request({"q": "zendegi"})

    @pytest.mark.parametrize(
        "arg,expectation",
        [
            ("b123456789", "12345678"),
            ("b12345678a", "12345678"),
            (123456789, "12345678"),
            ("123456789", "12345678"),
            ("12345678a", "12345678"),
            ("12345678", "12345678"),
        ],
    )
    def test_prep_sierra_number(self, arg, expectation):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            assert session._prep_sierra_number(arg) == expectation

    @pytest.mark.parametrize(
        "arg", ["bt12345678", "o12345678", "123456", "1234567890", 12345, "wlo12345"]
    )
    def test_prep_sierra_number_exceptions(self, arg):
        err_msg = "Invalid Sierra bib number passed."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session._prep_sierra_number(arg)
                assert err_msg in str(exc.value)

    def test_search_bibNo_success(self, mock_successful_session_get_response):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            response = session.search_bibNo("b123456789")
            assert response.status_code == 200

    @pytest.mark.parametrize("arg", [None, ""])
    def test_search_bibNo_empty_keyword(self, arg):
        err_msg = "Missing keyword argument."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.search_bibNo(arg)
                assert err_msg in str(exc.value)

    def test_search_bibNo_timeout(self, mock_timeout):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_bibNo("b123456789")

    def test_search_bibNo_connection_error(self, mock_connectionerror):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_bibNo("b123456789")

    def test_search_bibNo_unexpected_error(self, mock_unexpected_error):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_bibNo("b123456789")


@pytest.mark.webtest
class TestSolrSessionLiveService:
    """
    Runs tests against web endpoint of the BPL Solr platform
    """

    def test_send_custom_request(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            payload = {
                "q": "title:civil AND war",
                "fq": "ss_type:catalog",
                "fq": "material_type:Book",
                "rows": 2,
            }
            response = session._send_request(payload)
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=2&fq=material_type%3ABook&q=title%3Acivil+AND+war"
            )

    def test_search_bibNo(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_bibNo("b10000017a")
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=id%3A10000017&fl=id%2Ctitle%2Cauthor_raw%2CpublishYear%2Ccreated_date%2Cmaterial_type%2Ccall_number%2Cisbn%2Clanguage%2Ceprovider%2Cecontrolnumber%2Ceurl%2Cdigital_avail_type%2Cdigital_copies_owned"
            )
            assert response.json()["response"]["numFound"] == 1
            assert response.json()["response"]["docs"][0]["id"] == "10000017"
