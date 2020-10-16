# -*- coding: utf-8 -*-

"""
This module provides SolrSession class for requests to BPL Solr platform
"""

from typing import Tuple, Union

import requests


from . import __title__, __version__


class BplSolrError(Exception):
    pass


class SolrSession(requests.Session):
    """
    A session class that wraps requests to BPL Solr platform.
    """

    def __init__(
        self,
        authorization: str,
        base_url: str,
        agent: str = None,
        timeout: Union[int, float, Tuple[int, int], Tuple[float, float]] = None,
    ):
        """
        Args:
            authorization:          Client-Key
            agent:                  "User-agent" parameter to be passed in the request
                                    header; usage strongly encouraged
            timeout:                how long to wait for server to send data before
                                    giving up; default value is 3 seconds
        """
        requests.Session.__init__(self)

        self.authorization = authorization
        self.base_url = base_url
        self.agent = agent
        self.timeout = timeout

        # validate passed arguments
        if type(self.authorization) is not str or not self.authorization:
            raise BplSolrError(
                "Invalid authorization. Argument must be a Client-Key string."
            )

        if type(self.base_url) is not str or not base_url:
            raise BplSolrError(
                "Invalid base_url argument. It must be a Client-Key string."
            )

        if not self.agent:
            self.agent = f"{__title__}/{__version__}"
        elif type(self.agent) is not str:
            raise BplSolrError("Invalid type of an agent argument.")
