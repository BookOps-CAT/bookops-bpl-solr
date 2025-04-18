# -*- coding: utf-8 -*-

"""
This module provides SolrSession class for requests to BPL Solr platform
"""

import sys
from typing import Dict, List, Optional, Tuple, Union

import requests


from . import __title__, __version__


class BookopsSolrError(Exception):
    pass


class SolrSession(requests.Session):
    """
    A session class that wraps requests to BPL Solr platform.
    """

    DEFAULT_RESPONSE_FIELDS = [
        "id",
        "title",
        "author_raw",
        "publishYear",
        "created_date",
        "material_type",
        "call_number",
        "isbn",
        "language",
        "eprovider",
        "econtrolnumber",
        "eurl",
        "digital_avail_type",
        "digital_copies_owned",
    ]

    def __init__(
        self,
        authorization: str,
        endpoint: str,
        agent: Optional[str] = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float], None] = (
            3,
            3,
        ),
    ):
        """
        Args:
            authorization:          Client-Key
            endpoint:               endpoint's URL
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 3 seconds
        """
        super().__init__()

        self.authorization = authorization
        self.endpoint = endpoint
        self.agent = agent
        self.timeout = timeout

        # validate passed arguments
        if not isinstance(self.authorization, str) or not self.authorization:
            raise BookopsSolrError(
                "Invalid authorization. Argument must be a Client-Key string."
            )

        if not isinstance(self.endpoint, str) or not self.endpoint:
            raise BookopsSolrError(
                "Invalid endpoint argument. It must be a Client-Key string."
            )

        if not self.agent:
            self.agent = f"{__title__}/{__version__}"
        elif not isinstance(self.agent, str):
            raise BookopsSolrError("Invalid type of an agent argument.")

        # set session headers
        self.headers.update({"Client-Key": self.authorization})
        self.headers.update({"User-Agent": self.agent})

    def _determine_response_fields(
        self,
        default_response_fields: bool,
        response_fields: Union[str, List[str], None],
    ) -> Union[str, None]:
        """Determines which fields to return in the response"""
        if default_response_fields:
            response_fields = self._prep_response_fields(self.DEFAULT_RESPONSE_FIELDS)
        elif response_fields is not None and not default_response_fields:
            response_fields = self._prep_response_fields(response_fields)
        return response_fields

    def _merge_with_payload_defaults(self, payload: Dict) -> Dict:
        """
        Merges user's payload with default parameters. User's values
        overwrite default values.
        """
        default_payload = {
            "rows": 10,
            "fq": "ss_type:catalog",  # to retrieve only catalog records
        }

        return {**default_payload, **payload}

    def _prep_response_fields(self, response_fields: Union[str, List[str]]) -> str:
        """
        Formats as comma separated string response fields passed as a list
        """
        if isinstance(response_fields, list):
            return ",".join(response_fields)
        elif isinstance(response_fields, str):
            return response_fields
        else:
            raise BookopsSolrError("Invalid type of 'reposponse_format' argument.")

    def _prep_sierra_number(self, bid: Union[str, int]) -> str:
        """
        Strips b prefix and removes last check digit

        Args:
            bid:                    Sierra bib number as string or int

        Returns:
            bid
        """
        err_msg = "Invalid Sierra bib number passed."

        if isinstance(bid, int):
            bid = str(bid).strip()

        if bid.lower()[0] == "b":
            bid = bid[1:]
        if len(bid) == 8:
            if not bid.isdigit():
                raise BookopsSolrError(err_msg)
        elif len(bid) == 9:
            bid = bid[:8]
            if not bid.isdigit():
                raise BookopsSolrError(err_msg)
        else:
            raise BookopsSolrError(err_msg)

        return bid

    def _send_request(
        self, payload: Optional[Dict] = None, hooks: Optional[Dict] = None
    ) -> requests.Response:
        """
        Prepares and sends GET request with given parameters (payload) to BPL Solr.
        Private method but can be used for ad hoc searches not provided in SolrSession
        direct query methods.
        Passed payload overrides default values.

        Args:
            payload:                query parameters as dictionary
            hooks:                  Requests library hook system that can be
                                    used for signal event handling, see more at:
                                    https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` instance


        Example:
            payload = {
                "q": "material_type:eBook AND digital_copies_owned:0"
                "start": 0,
                "rows": 50,
                "fq": "ss_type:catalog",
                "fl": "id,title,econtrolnumber,eurl"
            }
            response = session._search(payload)
        """

        if not isinstance(payload, dict) or not payload:
            raise BookopsSolrError("Missing or invalid payload argument.")

        payload = self._merge_with_payload_defaults(payload)

        try:
            response = self.get(
                self.endpoint, params=payload, timeout=self.timeout, hooks=hooks
            )
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise BookopsSolrError(f"Connection error: {sys.exc_info()[0]}")

        except Exception:
            raise BookopsSolrError(f"Unexpected error: {sys.exc_info()[0]}")

    def search_bibNo(
        self,
        keyword: Union[str, int],
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves documents with matching id (Sierra bib #)

        Args:
            keyword:                    Sierra bib number as str with or without 'b'
                                        prefix or last 9th check digit, or as int with
                                        or without 9th check digit
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object


        """
        if not keyword:
            raise BookopsSolrError("Missing keyword argument.")

        # verify and prep bib number
        keyword = self._prep_sierra_number(keyword)

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {"q": f"id:{keyword}", "fl": response_fields}

        response = self._send_request(payload, hooks)

        return response

    def search_controlNo(
        self,
        keyword: str,
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves documents with matching control number (001 MARC tag).

        Args:
            keyword:                    control number as str
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """
        if not isinstance(keyword, str):
            raise BookopsSolrError("Control number keyword must be a string.")

        if not keyword:
            raise BookopsSolrError("Provided empty string as control number keyword.")

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {
            "q": f"ss_marc_tag_001:{keyword}",
            "fl": response_fields,
        }

        response = self._send_request(payload, hooks)

        return response

    def search_isbns(
        self,
        keywords: List[str],
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves documents with matching ISBNs.

        Args:
            keywords:                   list of ISBN strings
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        if not isinstance(keywords, list):
            raise BookopsSolrError("ISBN keywords argument must be a list.")

        if not keywords:
            raise BookopsSolrError("ISBN keywords argument is an empty list.")

        # prep multiple ISBNs
        keywords_str = " OR ".join(keywords)

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {
            "q": f"isbn:{keywords_str}",
            "fl": response_fields,
        }

        response = self._send_request(payload, hooks)

        return response

    def search_reserveId(
        self,
        keyword: str,
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves documents with matching reserve ID

        Args:
            keyword:                    Overdrive reserve ID string
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        if not isinstance(keyword, str):
            raise BookopsSolrError("Reserve id keyword argument must be a string.")

        if not keyword:
            raise BookopsSolrError("Missing reserve id keyword argument.")

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {"q": f"econtrolnumber:{keyword}", "fl": response_fields}

        response = self._send_request(payload, hooks)

        return response

    def search_upcs(
        self,
        keywords: List[str],
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves documents with matching UPCs.

        Args:
            keywords:                   list of UPC strings
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        if not isinstance(keywords, list):
            raise BookopsSolrError("UPC keywords argument must be a list.")

        if not keywords:
            raise BookopsSolrError("UPC keywords argument is an empty list.")

        # prep multiple UPCs
        keywords_str = " OR ".join(keywords)

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {
            "q": f"sm_marc_tag_024_a:{keywords_str}",
            "fl": response_fields,
        }

        response = self._send_request(payload, hooks)

        return response

    def find_expired_econtent(
        self,
        rows: int = 50,
        result_page: int = 0,
        default_response_fields: bool = True,
        response_fields: Union[str, List[str], None] = None,
        hooks: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Retrieves Overdrive e-content documents that expired and library has no longer
        access to.
        By default returns 50 documents per page

        Args:
            rows:                       number of retrieved documents per response page
            result_page:                page of retrieved results
            default_response_fields:    when True returns only predetermined fields,
                                        when False returns all fields unless specified
                                        in `response_fields` argument
            response_fields:            fields to be returned as comma separated string,
                                        or a list of strings
            hooks:                      Requests library hook system that can be
                                        used for signal event handling, see more at:
                                        https://requests.readthedocs.io/en/master/user/advanced/#event-hooks

        Returns:
            `requests.Response` object
        """

        if not isinstance(rows, int) or not isinstance(result_page, int):
            raise BookopsSolrError("Invalid type of arguments passed.")

        if rows < 1 or rows > 100:
            raise BookopsSolrError(
                "Rows argument must be bigger than 1 and no larger than 100."
            )

        # determine if pass default, custom, or allow all fields in response
        response_fields = self._determine_response_fields(
            default_response_fields, response_fields
        )

        payload = {
            "q": "digital_copies_owned:0 AND digital_avail_type:Normal",
            "rows": rows,
            "start": result_page,
            "fl": response_fields,
        }

        response = self._send_request(payload, hooks)

        return response
