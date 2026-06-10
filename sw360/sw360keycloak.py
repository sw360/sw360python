# -------------------------------------------------------------------------------
# Copyright (c) 2026 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from datetime import datetime
from typing import Optional

import jwt
import requests

from .sw360error import SW360Error


class SW360Keycloak:
    """SW360 Keycloak Authentication

    This class extends the SW360 class to support authentication using Keycloak.
    It retrieves the necessary credentials from a configuration file and obtains an
    access token from Keycloak to authenticate with the SW360 API.

    :param url: URL of the SW360 instance
    :type url: string
    """

    def __init__(self, url: str) -> None:
        if url[-1] != "/":
            url += "/"
        self.url: str = url

    def get_keycloak_token(self, client_id: str, client_secret: str, write_access: bool = False) -> Optional[str]:
        """
        Gets a token for REST API access to SW360 from the Keycloak server. The token is obtained using the
        client credentials grant type, which requires a client_id and client_secret. The token can be used
        for authentication when accessing the SW360 REST API. If write_access is True, the token will have
        permissions to perform write operations on SW360, otherwise it will only have read access.

        :param client_id: the SW360 client_id to be used for token generation
        :type client_id: str
        :param client_secret: the SW360 client_secret to be used for token generation
        :type client_secret: str
        :param write_access: whether the token should have write access
        :type write_access: bool
        :return: the generate token
        :rtype: string or None if there was an error obtaining the token
        """
        token_endpoint = self.url + "kc/realms/sw360/protocol/openid-connect/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        scope = "email profile"
        if write_access:
            scope += " WRITE"  # must be uppercase!

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope
        }

        response = requests.post(token_endpoint, headers=headers, data=data)
        if response.ok:
            token_response = response.json()
            return token_response.get("access_token")

        raise SW360Error(response, token_endpoint, message="Unable to obtain token from Keycloak")

    def is_token_expired(self, token: str) -> bool:
        """
        Checks if the given JWT token is expired.

        :param token: the JWT token to check
        :type token: str
        :return: True if the token is expired, False otherwise
        :rtype: bool
        """

        try:
            # alg = RS256
            decoded = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
            # print(decoded)
            # {
            #   'exp': 1776699510,
            #   'iat': 1702769910,
            #   'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            #   'iss': 'https://stage.sw360.com/kc/realms/sw360',
            #   'aud': 'account',
            #   'sub': 'xxx',
            #   'typ': 'Bearer',
            #   'azp': 'yyy',
            #   'acr': '1',
            #   'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            #   'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            #   'scope': ''READ profile email'',
            #   'clientHost': '192.168.146.160'
            #   'email_verified': False,
            #   'preferred_username': 'service-account-zzzz',
            #   'clientAddress': '192.168.146.160',
            #   'email': 'john.doe@sw360.com',
            #   'client_id': 'xxx'
            # }
        except Exception as ex:
            raise SW360Error(message="Unable to analyze token: " + repr(ex))

        if "exp" in decoded:
            exp_seconds = int(decoded["exp"])
            exp = datetime.fromtimestamp(exp_seconds)
            return exp < datetime.now()
        else:
            raise SW360Error(message="Unable to analyze token: exp field missing!")

    def is_write_token(self, token: str) -> bool:
        """
        Checks if the given JWT token has write access.

        :param token: the JWT token to check
        :type token: str
        :return: True if the token has write access, False otherwise
        :rtype: bool
        """

        try:
            # alg = RS256
            decoded = jwt.decode(token, algorithms=["HS256"], options={"verify_signature": False})
        except Exception as ex:
            raise SW360Error(message="Unable to analyze token: " + repr(ex))

        if "scope" in decoded:
            scope = decoded["scope"]
            return scope.lower().find("write") >= 0
        else:
            raise SW360Error(message="Unable to analyze token: scope field missing!")
