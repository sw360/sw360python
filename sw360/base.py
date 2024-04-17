# -------------------------------------------------------------------------------
# Copyright (c) 2024 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

# import urllib.parse
from typing import Any, Dict, Optional, Tuple

import requests

from .sw360error import SW360Error


class BaseMixin():
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

    def __init__(self, url: str, token: str, oauth2: bool = False) -> None:
        """Constructor"""
        if url[-1] != "/":
            url += "/"
        self.url = url
        self.session: Optional[requests.Session] = None

        if oauth2:
            self.api_headers = {"Authorization": "Bearer " + token}
        else:
            self.api_headers = {"Authorization": "Token " + token}

        self.force_no_session = False

    def api_get(self, url: str = "") -> Optional[Dict[str, Any]]:
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
            if self.session:
                response = self.session.get(url)

        if response.ok:
            if response.status_code == 204:  # 204 = no content
                return None
            return response.json()

        raise SW360Error(response, url)

    # type checking: not for Python 3.8: tuple[Optional[Any], Dict[str, Dict[str, str]], bool]
    def _update_external_ids(self, current_data: Dict[str, Any], ext_id_name: str, ext_id_value: str,
                             update_mode: str) -> Tuple[Optional[Any], Dict[str, Dict[str, str]], bool]:
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

    @classmethod
    def get_id_from_href(cls, href: str) -> str:
        """Extracts the identifier from the href and returns it

        :param href: HAL href for a specific resource
        :type href: string (valid URL)
        :return: the id part of the href
        :rtype: string
        """

        pos = href.rfind("/")
        identifier = href[(pos + 1):]
        return identifier

    @classmethod
    def url_encode(cls, text: str) -> str:
        """
        URL encodes the text, i.e. returns a string that can be properly
        use as part of a URL.
        Examples:
        * SI BP => SI%20BP

        In version 18 of SW360 URL encoding is not yet fully supported.
        """

        # disabled for the time being...
        # text = urllib.parse.quote(text)
        return text
