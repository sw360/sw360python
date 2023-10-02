# -------------------------------------------------------------------------------
# Copyright (c) 2019-2022 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

"""Python interface to the Siemens SW360 platform"""

import requests

from .sw360error import SW360Error

from .attachments import AttachmentsMixin
from .clearing import ClearingMixin
from .components import ComponentsMixin
from .license import LicenseMixin
from .project import ProjectMixin
from .releases import ReleasesMixin
from .vendor import VendorMixin
from .vulnerabilities import VulnerabilitiesMixin


class SW360(
    AttachmentsMixin,
    ClearingMixin,
    ComponentsMixin,
    LicenseMixin,
    ProjectMixin,
    ReleasesMixin,
    VendorMixin,
    VulnerabilitiesMixin
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
    """

    def __init__(self, url, token, oauth2=False):
        """Constructor"""
        if url[-1] != "/":
            url += "/"
        self.url = url
        self.session = None

        if oauth2:
            self.api_headers = {"Authorization": "Bearer " + token}
        else:
            self.api_headers = {"Authorization": "Token " + token}

        self.force_no_session = False

    def login_api(self, token=None):
        """Login to SW360 REST API. This used to have a `token` parameter
        due to historic reasons which is ignored.

        You need to call this before any other method accessing SW360.

        :raises SW360Error: if the login fails
        """
        if not self.force_no_session:
            self.session = requests.Session()
            self.session.headers = self.api_headers.copy()

        url = self.url + "resource/api/"
        try:
            if self.force_no_session:
                resp = requests.get(url, headers=self.api_headers)
            else:
                resp = self.session.get(url)

        except Exception as ex:
            raise SW360Error(None, url, message="Unable to login: " + repr(ex))

        if resp.ok:
            return True
        else:
            raise SW360Error(resp, url, message="Unable to login")

    def close_api(self):
        """A keep-alive HTTP session is used to access the SW360 REST API.
        This method allows to explicitely close the connection at a defined
        time. Normally, you don't need to call it - session is cleaned up
        automatically when needed."""
        if self.session is not None:
            self.session.close()
            self.session = None

    def api_get(self, url=None):
        """Request `url` from REST API and return json answer.

        :param url: the url to be requested
        :type url: string
        :return: JSON data
        :rtype: JSON
        :raises SW360Error: if there is a negative HTTP response
        """

        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.get(url, headers=self.api_headers)
        else:
            response = self.session.get(url)

        if response.ok:
            if response.status_code == 204:  # 204 = no content
                return None
            return response.json()

        raise SW360Error(response, url)

    def api_get_raw(self, url=None):
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
            response = self.session.get(url)

        if response.ok:
            return response.text

        raise SW360Error(response, url)

    def _update_external_ids(self, current_data, ext_id_name, ext_id_value,
                             update_mode):
        """Internal helper function to prepare an update/addition of external
        id while preserving the others."""
        old_value = None
        if "externalIds" not in current_data:
            ext_id_data = {"externalIds": {ext_id_name: ext_id_value}}
        else:
            if ext_id_name in current_data["externalIds"]:
                old_value = current_data["externalIds"][ext_id_name]
            ext_id_data = {"externalIds": current_data["externalIds"]}
            ext_id_data["externalIds"][ext_id_name] = ext_id_value

        if update_mode == "delete":
            del ext_id_data["externalIds"][ext_id_name]

        if (update_mode == "overwrite"
                or (update_mode == "none" and old_value is None)
                or (update_mode == "delete" and old_value is not None)):
            update = True
        else:
            update = False

        return (old_value, ext_id_data, update)

    def _add_param(self, url: str, param: str) -> str:
        """Add the given parameter to the given url"""
        if "?" in url:
            url = url + "&"
        else:
            url = url + "?"

        return url + param

    # ----- Health -------------------------------------------------------

    def get_health_status(self):
        """Get information about the service's health.

        API endpoint: GET /health

        :return: service health status
        :rtype: JSON health status object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/health/")
        return resp

    # ----- Support ----------------------------------------------------------

    @classmethod
    def get_id_from_href(cls, href):
        """"Extracts the identifier from the href and returns it

        :param href: HAL href for a specific resource
        :type href: string (valid URL)
        :return: the id part of the href
        :rtype: string
        """

        pos = href.rfind("/")
        identifier = href[(pos + 1):]
        return identifier
