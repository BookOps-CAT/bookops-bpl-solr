# -*- coding: utf-8 -*-

"""
This module provides SolrSession class for requests to BPL Solr platform
"""

import sys
from typing import Dict, List, Tuple, Type, Union

import requests


from . import __title__, __version__


class BookopsSolrError(Exception):
    pass


class SolrSession(requests.Session):
    """
    A session class that wraps requests to BPL Solr platform.
    """

    def __init__(
        self,
        authorization: str,
        endpoint: str,
        agent: str = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float]] = None,
    ):
        """
        Args:
            authorization:          Client-Key
            endopint:               endpoint's URL
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 3 seconds
        """
        requests.Session.__init__(self)

        self.authorization = authorization
        self.endpoint = endpoint
        self.agent = agent
        self.timeout = timeout

        # validate passed arguments
        if type(self.authorization) is not str or not self.authorization:
            raise BookopsSolrError(
                "Invalid authorization. Argument must be a Client-Key string."
            )

        if type(self.endpoint) is not str or not self.endpoint:
            raise BookopsSolrError(
                "Invalid endpoint argument. It must be a Client-Key string."
            )

        if not self.agent:
            self.agent = f"{__title__}/{__version__}"
        elif type(self.agent) is not str:
            raise BookopsSolrError("Invalid type of an agent argument.")

        # set session headers
        self.headers.update({"Client-Key": self.authorization})
        self.headers.update({"User-Agent": self.agent})

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

    def _prep_sierra_number(self, bid: Union[str, int]) -> str:
        """
        Strips b prefix and removes last check digit

        Args:
            bid:                    Sierra bib number as string or int

        Returns:
            bid
        """
        err_msg = "Invalid Sierra bib number passed."

        if type(bid) is int:
            bid = str(bid)

        if "b" == bid.lower()[0]:
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
        self, payload: Dict = None, hooks: Dict = None
    ) -> Type[requests.Response]:
        """
        Prepares and sends GET request with given parameters (payload) to BPL Solr.
        Private method but can be used for ad hoc searches not provided in SolrSession
        direct query methods.
        Passed payload overrides default values.

        Args:
            payload:                query parameters as dictionary

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

        if type(payload) is not dict or not payload:
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

    def search_bibNo(self, keyword: Union[str, int]) -> Type[requests.Response]:
        """
        Retrieves documents with matching id (Sierra bib #)
        """
        pass

    def search_isbns(self, keywords: List[str]) -> Type[requests.Response]:
        """
        Retrieves documents with matching ISBNs.
        """
        pass

    def search_reserveId(self, keyword: str) -> Type[requests.Response]:
        pass
