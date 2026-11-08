# -------------------------------------------------------------------------------
# Copyright (c) 2019-2026 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
# Authors: mishra.gaurav@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

"""Python interface to the Siemens SW360 platform"""

from typing import Any, Callable, Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.auth import AuthBase
from requests.models import PreparedRequest
from urllib3.util.retry import Retry

from .attachments import AttachmentsMixin
from .clearing import ClearingMixin
from .components import ComponentsMixin
from .license import LicenseMixin
from .moderationrequests import ModerationRequestMixin
from .packages import PackagesMixin
from .project import ProjectMixin
from .releases import ReleasesMixin
from .reports import ReportsMixin
from .sw360error import SW360Error
from .sw360keycloak import KeycloakTokenProvider, SW360Keycloak
from .vendor import VendorMixin
from .vulnerabilities import VulnerabilitiesMixin

# Retry mechanism for rate limiting
adapter = HTTPAdapter(max_retries=Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True,
    backoff_factor=30,
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH"]
))
session_default = requests.Session()
session_default.mount("http://", adapter)
session_default.mount("https://", adapter)


class _TokenProviderAuth(AuthBase):
    """Sets the authorization header of each request from a token provider."""

    def __init__(self, token_provider: Callable[[], str], scheme: str) -> None:
        self.token_provider = token_provider
        self.scheme = scheme

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        request.headers["Authorization"] = f"{self.scheme} {self.token_provider()}"
        return request


class SW360(
    AttachmentsMixin,
    ClearingMixin,
    ComponentsMixin,
    LicenseMixin,
    ProjectMixin,
    ReleasesMixin,
    ReportsMixin,
    VendorMixin,
    VulnerabilitiesMixin,
    PackagesMixin,
    ModerationRequestMixin
):
    """Python interface to the Siemens SW360 platform

    Authentication against a running SW360 instance is performed using an API token.
    The token will be sent as HTTP header using the format
    `Authorization: <token_type> <token>`. Check your SW360 REST API
    documentation for details on needed type and how to get the token.
    token_type is "Bearer" for an OAuth workflow and "Token" for tokens
    generated via the SW360 UI.

    :param url: URL of the SW360 instance
    :param token: The SW360 REST API token (the cryptic string without
     "Authorization:" and `token_type`).
    :param oauth2: flag indicating whether this is an OAuth2 token
    :type url: string
    :type token: string
    :type oauth2: boolean
    :ivar default_batch_size: Default size of batch to use while fetching all items from API
    :type default_batch_size: int
    :ivar api_version: SW360 API Version, defaults to 18.0
    """

    def __init__(
        self,
        url: str,
        token: str = "",
        oauth2: bool = False,
        session: Optional[requests.Session] = session_default,
        default_batch_size: int = 50,
    ) -> None:
        """Constructor"""
        super().__init__(url, token, oauth2, default_batch_size)
        if url[-1] != "/":
            url += "/"
        self.url: str = url
        self.session: Optional[requests.Session] = session

        if oauth2:
            self.api_headers = {"Authorization": "Bearer " + token}
        else:
            self.api_headers = {"Authorization": "Token " + token}

        self.force_no_session = False
        self.default_batch_size = default_batch_size
        self.api_version = self.parse_version("18.0")

    def login_api(self, token: str = "") -> bool:  # noqa
        """Login to SW360 REST API. This used to have a `token` parameter
        due to historic reasons which is ignored.

        You need to call this before any other method accessing SW360.

        :raises SW360Error: if the login fails
        """
        if not self.force_no_session:
            self.session.headers = self.api_headers.copy()  # type: ignore

        url = self.url + "resource/api/"
        try:
            if self.force_no_session:
                resp = requests.get(url, headers=self.api_headers)
            else:
                if self.session:
                    resp = self.session.get(url)

        except Exception as ex:
            raise SW360Error(None, url, message="Unable to login: " + repr(ex))

        version_url = self.url + "resource/api/version"
        try:
            if self.force_no_session:
                versp = requests.get(version_url,
                                     headers={"Accept": "application/json"})
            else:
                if self.session:
                    versp = self.session.get(
                        version_url,
                        headers={"Accept": "application/json"})
            version_response = versp.json()
            if "apiVersion" not in version_response:
                raise SW360Error(versp, version_url,
                                 "Unable to get API version")
            self.api_version = self.parse_version(version_response["apiVersion"])
        except Exception:
            self.api_version = self.parse_version("18.0")

        if resp.ok:
            return True
        else:
            raise SW360Error(resp, url, message="Unable to login")

    def close_api(self) -> None:
        """A keep-alive HTTP session is used to access the SW360 REST API.
        This method allows to explicitly close the connection at a defined
        time. Normally, you don't need to call it - session is cleaned up
        automatically when needed."""
        if self.session:
            self.session.close()
            self.session = None

    def api_get_raw(self, url: str = "") -> str:
        """Request `url` from REST API and return raw result.

        :param url: the url to be requested
        :type url: string
        :return: the HTTP response
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.get(url, headers=self.api_headers)
        else:
            if self.session:
                response = self.session.get(url)

        if response.ok:
            return response.text

        raise SW360Error(response, url)

    # ----- Health -------------------------------------------------------

    def get_health_status(self) -> Optional[Dict[str, Any]]:
        """Get information about the service's health.

        API endpoint: GET /health

        :return: service health status
        :rtype: JSON health status object
        :raises SW360Error: if there is a negative HTTP response
        """
        if self.is_above_version_18():
            return self.api_get(self.url + "resource/api/health")
        else:
            return self.api_get(self.url + "resource/health/")

    @staticmethod
    def parse_version(version_string: str) -> Tuple[int, int]:
        """Extract major.minor as comparable tuple"""
        parts = version_string.split('.')
        return (int(parts[0]), int(parts[1]))


class SW360KeycloakClient(SW360):
    """Python interface to the Siemens SW360 platform, authenticating via Keycloak.

    In contrast to `SW360`, this client is given the Keycloak credentials instead
    of a token. It obtains the token itself and renews it shortly before it
    expires, so that operations running longer than the token lifetime do not
    fail. `SW360` and its static token usage are not affected by this class.

    Unless a session is passed in, the client creates its own session, so that
    the session shared by `SW360` instances is left unchanged. A session passed
    in by the caller will have its authentication configured by this client.

    :param url: URL of the SW360 instance
    :param client_id: the SW360 client_id to be used for token generation
    :param client_secret: the SW360 client_secret to be used for token generation
    :param write_access: whether the token should have write access
    :param session: the session to use, a new one is created if not given
    :param refresh_before_seconds: how long before expiry a token gets renewed
    :type url: string
    :type client_id: string
    :type client_secret: string
    :type write_access: boolean
    :type session: requests.Session
    :type refresh_before_seconds: int
    :raises SW360Error: if no token could be obtained from Keycloak
    """

    def __init__(
        self,
        url: str,
        client_id: str,
        client_secret: str,
        write_access: bool = False,
        session: Optional[requests.Session] = None,
        default_batch_size: int = 50,
        refresh_before_seconds: int = 300,
    ) -> None:
        """Constructor"""
        self._keycloak_token_provider = KeycloakTokenProvider(
            SW360Keycloak(url),
            client_id,
            client_secret,
            write_access=write_access,
            refresh_before_seconds=refresh_before_seconds,
        )
        initial_token = self._keycloak_token_provider()

        if session is None:
            session = requests.Session()
            session.mount("http://", adapter)
            session.mount("https://", adapter)

        super().__init__(
            url=url,
            token=initial_token,
            oauth2=True,
            session=session,
            default_batch_size=default_batch_size,
        )
        if self.session is not None:
            self.session.auth = _TokenProviderAuth(self._keycloak_token_provider, "Bearer")

    @property
    def current_token(self) -> str:
        """The access token currently in use, renewed first if it is about to
        expire. Use this if you need to pass the token on, for example to
        another component creating its own client.

        :return: a currently valid access token
        :rtype: str
        :raises SW360Error: if no token could be obtained from Keycloak
        """
        return self._keycloak_token_provider()

    @property
    def api_headers(self) -> Dict[str, str]:
        """The HTTP headers to use for requests that do not go through the
        session, with a token that is valid now."""
        headers = self._api_headers.copy()
        headers["Authorization"] = "Bearer " + self._keycloak_token_provider()
        return headers

    @api_headers.setter
    def api_headers(self, headers: Dict[str, str]) -> None:
        # the base constructor sets the initial static header, the getter
        # replaces its token on every read
        self._api_headers = headers
