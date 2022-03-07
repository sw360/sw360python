# -------------------------------------------------------------------------------
# (c) 2022 BMW CarIT GmbH
# All Rights Reserved.
# Authors: helio.chissini-de-castro@bmw.de
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict

from .sw360error import SW360Error


class SW360OAuth2:
    """SW360 OAuth2 Credentials
    Restore or create Sw360 oauth2 tokens from user/password if auth server is alive
    :param url: URL of the SW360 instance
    :param user: SW360 username
    :param password: SW360 password
    :type url: string
    :type user: string
    :type password: string
    """

    _client_id: str
    _client_secret: str
    _user: str
    _password: str
    _token: str
    _refresh_token: str

    def __init__(self, url: str, user: str, password: str):
        self._url, self._user, self._password = url, user, password
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.__get_credentials()

    def __get_credentials(self) -> None:
        """Return last valid credentials id and secret

        Raises:
            SW360Error: If is unable to authorize
        """
        data: Dict[str, Any]
        url = urljoin(self._url, "/authorization/client-management")
        auth = HTTPBasicAuth(self._user, self._password)

        try:
            response = requests.get(url, verify=False, auth=auth)
        except Exception as ex:
            raise SW360Error(None, url, message="Unable to connect to oauth2 service: " + repr(ex))

        data = response.json()[0]
        self._client_id = data["client_id"]
        self._client_secret = data["client_secret"]

    def create_client(self, description: str, writeable: False) -> None:
        """Create an OAuth2 client

        Args:
            description (str): Some description of the client
            writeable (bool): Create the id read/writeable

        Raises:
            SW360Error: When unable to create a client
        """
        scope = ["READ"]
        if writeable:
            scope.append("WRITE")
        payload: Union[str, Any] = {
            "description": description,
            "authorities": ["BASIC"],
            "scope": scope,
            "access_token_validity": 3600,
            "refresh_token_validity": 3600,
        }
        auth = HTTPBasicAuth(self._user, self._password)
        headers = {"content-type": "application/json"}
        url = urljoin(self._url, "/authorization/client-management")

        try:
            requests.post(url, json=payload, verify=False, auth=auth, headers=headers)
        except Exception as ex:
            raise SW360Error(None, url, message="Cant create oauth client: " + repr(ex))

    def generate_token(self) -> str:
        """Generate a new bearer token
        """
        self.__oauth_token(True)

    def __token(self, create: bool = False) -> None:
        """Create or return Liferay Token
        :param create: If should create or restore active tokens
        :type create: bool
        """
        data: Dict[str, Any]
        url = urljoin(self._url, "/authorization/oauth/token")
        payload: Dict[str, Any] = {
            "grant_type": "password",
            "username": self._user,
            "password": self._password,
        }
        auth = HTTPBasicAuth(self._client_id, self._client_secret)

        headers: CaseInsensitiveDict[Any] = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        if create:
            response = requests.post(url, auth=auth, headers=headers, json=payload, verify=False)
        else:
            params = f"grant_type=password&username={self._user}&password={self._password}"
            response = requests.get(url, auth=auth, headers=headers, params=params, verify=False)

        data = response.json()
        self._token = data["access_token"]
        self._refresh_token = data["refresh_token"]

    @property
    def token(self) -> Optional[str]:
        """Return the valid oauth token"""
        self.__token()
        return self._token

    @property
    def refresh_token(self) -> str:
        """Return the valid oauth refresh token"""
        self.__token()
        return self._refresh_token

    @property
    def url(self) -> str:
        """Return current session object url"""
        return self._url
