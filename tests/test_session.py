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
        "arg_def,arg_field,expectation",
        [
            (
                True,
                None,
                "id,title,author_raw,publishYear,created_date,material_type,call_number,isbn,language,eprovider,econtrolnumber,eurl,digital_avail_type,digital_copies_owned",
            ),
            (
                False,
                "field1,field2",
                "field1,field2",
            ),
            (False, None, None),
        ],
    )
    def test_determine_response_fields(self, arg_def, arg_field, expectation):
        session = SolrSession("my_client_key", "example.com")
        assert (
            session._determine_response_fields(
                default_response_fields=arg_def, response_fields=arg_field
            )
            == expectation
        )
        session.close()

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
        session.close()

    @pytest.mark.parametrize(
        "arg,expectation", [(["a", "b", "c"], "a,b,c"), ("a,b,c", "a,b,c")]
    )
    def test_prep_response_fields(self, arg, expectation):
        session = SolrSession("my_client_key", "example.com")
        assert session._prep_response_fields(arg) == expectation
        session.close()

    @pytest.mark.parametrize("arg", [None, 1234])
    def test_prep_response_fields_exception(self, arg):
        err_msg = "Invalid type of 'reposponse_format' argument."
        session = SolrSession("my_client_key", "example.com")
        with pytest.raises(BookopsSolrError) as exc:
            session._prep_response_fields(arg)
        assert err_msg in str(exc.value)
        session.close()

    @pytest.mark.parametrize("arg", [({}, None, "some_str")])
    def test_send_request_payload_errors(self, arg):
        err_msg = "Missing or invalid payload argument."
        session = SolrSession("my_client_key", "example.com")
        with pytest.raises(BookopsSolrError) as exc:
            session._send_request(arg)
        assert err_msg in str(exc.value)
        session.close()

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

    def test_search_isbns_success(self, mock_successful_session_get_response):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            response = session.search_isbns(["9781680502404"])
            assert response.status_code == 200

    @pytest.mark.parametrize("arg", [None, ""])
    def test_search_isbns_invalid_keywords_type(self, arg):
        err_msg = "ISBN keywords argument must be a list."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.search_isbns(arg)
            assert err_msg in str(exc.value)

    def test_search_isbns_empty_list(self):
        err_msg = "Missing keywords argument."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.search_isbns([])
            assert err_msg in str(exc.value)

    def test_search_isbns_timeout(self, mock_timeout):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_isbns(["9781680502404"])

    def test_search_isbns_connection_error(self, mock_connectionerror):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_isbns(["9781680502404"])

    def test_search_isbns_unexpected_error(self, mock_unexpected_error):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_isbns(["9781680502404"])

    def test_search_reserveId_success(self, mock_successful_session_get_response):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            response = session.search_reserveId("some_string")
            assert response.status_code == 200

    @pytest.mark.parametrize("arg", [None, [], 1234])
    def test_search_reserveId_invalid_keyword(self, arg):
        err_msg = "Reserve id keyword argument must be a string."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.search_reserveId(arg)
            assert err_msg in str(exc.value)

    def test_search_reserveId_empty_keyword(self):
        err_msg = "Missing reserve id keyword argument."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.search_reserveId("")
            assert err_msg in str(exc.value)

    def test_search_reserveId_timeout(self, mock_timeout):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_reserveId("some_string")

    def test_search_reserveId_connection_error(self, mock_connectionerror):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_reserveId("some_string")

    def test_search_reserveId_unexpected_error(self, mock_unexpected_error):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.search_reserveId("some_string")

    def test_find_expired_econtent_success(self, mock_successful_session_get_response):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            response = session.find_expired_econtent()
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "arg1,arg2",
        [
            (None, None),
            ("foo", 1),
            (1, "foo"),
        ],
    )
    def test_find_expired_econtent_invalid_args(self, arg1, arg2):
        err_msg = "Invalid type of arguments passed."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.find_expired_econtent(rows=arg1, result_page=arg2)
            assert err_msg in str(exc.value)

    @pytest.mark.parametrize("arg", [0, 101, -3])
    def test_find_expired_econtent_too_many_rows(
        self, arg, mock_successful_session_get_response
    ):
        err_msg = "Rows argument must be bigger than 1 and no larger than 100."
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError) as exc:
                session.find_expired_econtent(rows=arg)
            assert err_msg in str(exc.value)

    def test_find_expired_econtent_timeout(self, mock_timeout):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.find_expired_econtent()

    def test_find_expired_econtent_connection_error(self, mock_connectionerror):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.find_expired_econtent()

    def test_find_expired_econtent_unexpected_error(self, mock_unexpected_error):
        with SolrSession(
            authorization="my_client_key", endpoint="example.com"
        ) as session:
            with pytest.raises(BookopsSolrError):
                session.find_expired_econtent()


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
            assert "Client-Key" in response.request.headers
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

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=id%3A10000017&fl=id%2Ctitle%2Cauthor_raw%2CpublishYear%2Ccreated_date%2Cmaterial_type%2Ccall_number%2Cisbn%2Clanguage%2Ceprovider%2Cecontrolnumber%2Ceurl%2Cdigital_avail_type%2Cdigital_copies_owned"
            )
            assert response.json()["response"]["numFound"] == 1
            assert response.json()["response"]["docs"][0]["id"] == "10000017"

    def test_search_bibNo_for_nonexistent_bib(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_bibNo(
                "b10000001a", default_response_fields=False, response_fields="id,title"
            )

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=id%3A10000001&fl=id%2Ctitle"
            )
            assert response.json() == {
                "response": {
                    "numFound": 0,
                    "start": 0,
                    "numFoundExact": True,
                    "docs": [],
                }
            }

    def test_search_bibNo_full_response_fields(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_bibNo("b10000017a", default_response_fields=False)

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=id%3A10000017"
            )
            assert response.json()["response"]["numFound"] == 1
            assert response.json()["response"]["docs"][0]["id"] == "10000017"

    def test_search_isbns(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_isbns(
                ["9780810984912", "9781419741890", "0810984911"]
            )

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=isbn%3A9780810984912+OR+9781419741890+OR+0810984911&fl=id%2Ctitle%2Cauthor_raw%2CpublishYear%2Ccreated_date%2Cmaterial_type%2Ccall_number%2Cisbn%2Clanguage%2Ceprovider%2Cecontrolnumber%2Ceurl%2Cdigital_avail_type%2Cdigital_copies_owned"
            )

    def test_search_isbns_empty(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_isbns(
                ["978081098491"]
            )  # last chr from isbns is missing

            assert response.status_code == 200
            assert response.json() == {
                "response": {
                    "numFound": 0,
                    "start": 0,
                    "numFoundExact": True,
                    "docs": [],
                }
            }

    def test_search_reserveId(self, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.search_reserveId("8CD53ED9-CEBD-4F78-8BEF-20A58F6F3857")

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == "https://www.bklynlibrary.org/solr/api/select/?rows=10&fq=ss_type%3Acatalog&q=econtrolnumber%3A8CD53ED9-CEBD-4F78-8BEF-20A58F6F3857&fl=id%2Ctitle%2Cauthor_raw%2CpublishYear%2Ccreated_date%2Cmaterial_type%2Ccall_number%2Cisbn%2Clanguage%2Ceprovider%2Cecontrolnumber%2Ceurl%2Cdigital_avail_type%2Cdigital_copies_owned"
            )

    @pytest.mark.parametrize("arg1,arg2", [(5, 0), (5, 1), (3, 2)])
    def test_find_expired_econtent(self, arg1, arg2, live_key):
        with SolrSession(
            authorization=live_key.client_key, endpoint=live_key.endpoint
        ) as session:
            response = session.find_expired_econtent(rows=arg1, result_page=arg2)

            assert "Client-Key" in response.request.headers
            assert response.status_code == 200
            assert (
                response.url
                == f"https://www.bklynlibrary.org/solr/api/select/?rows={arg1}&fq=ss_type%3Acatalog&q=digital_copies_owned%3A0+AND+digital_avail_type%3ANormal&start={arg2}&fl=id%2Ctitle%2Cauthor_raw%2CpublishYear%2Ccreated_date%2Cmaterial_type%2Ccall_number%2Cisbn%2Clanguage%2Ceprovider%2Cecontrolnumber%2Ceurl%2Cdigital_avail_type%2Cdigital_copies_owned"
            )
