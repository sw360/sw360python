# -------------------------------------------------------------------------------
# Copyright (c) 2026 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
import unittest
import warnings
from datetime import datetime

import jwt
import responses

sys.path.insert(1, "..")

from sw360 import SW360Error  # noqa: E402
from sw360.sw360keycloak import SW360Keycloak  # noqa: E402


class Sw360TestKeycloak(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self) -> None:
        warnings.filterwarnings(
            "ignore", category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

    def _add_login_response(self) -> None:
        """
        Add the response for a successful login.
        """
        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

    @responses.activate
    def test_get_keycloak_read_token(self) -> None:
        responses.add(
            responses.POST,
            url=self.MYURL + "kc/realms/sw360/protocol/openid-connect/token",
            json={"access_token": "my_mock_access_token"},
            status=200,
            match=[
                responses.matchers.urlencoded_params_matcher({
                    "grant_type": "client_credentials",
                    "client_id": "mock_client_id",
                    "client_secret": "mock_client_secret",
                    "scope": "email profile"
                })
            ]
        )

        lib = SW360Keycloak(self.MYURL)
        actual = lib.get_keycloak_token("mock_client_id", "mock_client_secret", False)
        self.assertIsNotNone(actual)
        self.assertEqual(actual, "my_mock_access_token")

    @responses.activate
    def test_get_keycloak_write_token(self) -> None:
        responses.add(
            responses.POST,
            url="https://my.server.com/kc/realms/sw360/protocol/openid-connect/token",
            json={"access_token": "my_mock_write_access_token"},
            status=200,
            match=[
                responses.matchers.urlencoded_params_matcher({
                    "grant_type": "client_credentials",
                    "client_id": "mock_client_id",
                    "client_secret": "mock_client_secret",
                    "scope": "email profile WRITE"
                })
            ]
        )

        lib = SW360Keycloak("https://my.server.com")  # without trailing dash
        actual = lib.get_keycloak_token("mock_client_id", "mock_client_secret", True)
        self.assertIsNotNone(actual)
        self.assertEqual(actual, "my_mock_write_access_token")

    def test_is_token_expired_yes(self) -> None:
        # create a JWT token
        # set expiration date to 10 seconds in the past
        expiration_date = datetime.now().timestamp() - 10
        test_token = jwt.encode({
            'exp': expiration_date,
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'scope': 'READ profile email',
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        result = lib.is_token_expired(test_token)
        self.assertTrue(result)

    @responses.activate
    def test_get_keycloak_token_error(self) -> None:
        responses.add(
            responses.POST,
            url=self.MYURL + "kc/realms/sw360/protocol/openid-connect/token",
            json={"error": "unauthorized_client"},
            status=401,
        )

        lib = SW360Keycloak(self.MYURL)
        with self.assertRaises(SW360Error):
            lib.get_keycloak_token("invalid_client_id", "invalid_client_secret", False)

    def test_is_token_expired_no(self) -> None:
        # create a JWT token
        expiration_date = datetime.now().timestamp() + 60
        test_token = jwt.encode({
            'exp': expiration_date,
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'scope': 'READ profile email',
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        result = lib.is_token_expired(test_token)
        self.assertFalse(result)

    def test_is_token_expired_invalid_token1(self) -> None:
        lib = SW360Keycloak(self.MYURL)
        with self.assertRaises(SW360Error) as context:
            lib.is_token_expired("test_token")

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Unable to analyze token:"))

    def test_is_token_expired_invalid_token2(self) -> None:
        # create a JWT token without exp field
        test_token = jwt.encode({
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'scope': 'READ profile email',
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        with self.assertRaises(SW360Error) as context:
            lib.is_token_expired(test_token)

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Unable to analyze token: exp field missing!"))

    def test_is_write_token_no(self) -> None:
        # create a JWT token
        expiration_date = datetime.now().timestamp() + 60
        test_token = jwt.encode({
            'exp': expiration_date,
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'scope': 'READ profile email',
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        result = lib.is_write_token(test_token)
        self.assertFalse(result)

    def test_is_write_token_yes(self) -> None:
        # create a JWT token
        expiration_date = datetime.now().timestamp() + 60
        test_token = jwt.encode({
            'exp': expiration_date,
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'scope': 'READ profile WRITE email',
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        result = lib.is_write_token(test_token)
        self.assertTrue(result)

    def test_is_write_token_invalid1(self) -> None:
        # create a JWT token
        expiration_date = datetime.now().timestamp() + 60
        test_token = jwt.encode({
            'exp': expiration_date,
            'iat': 1702769910,
            'jti': 'trrtcc:6f1d3934-b319-1183-a059-8b7606f0a647',
            'iss': 'https://my.server.com/kc/realms/sw360',
            'aud': 'account',
            'sub': 'cf3fb608-4dba-42e0-bb89-7e13f995b931',
            'typ': 'Bearer',
            'azp': '7f75885d309970833f4187295d9babb8',
            'acr': '1',
            'realm_access': {'roles': ['default-roles-sw360', 'offline_access', 'uma_authorization']},
            'resource_access': {'account': {'roles': ['manage-account', 'manage-account-links', 'view-profile']}},
            'clientHost': '139.21.146.160',
            'email_verified': 'False',
            'preferred_username': 'service-account-xxx5885d309970833f4187295d9babb8',
            'clientAddress': '127.0.0.1',
            'email': 'john.doe@somewhere.com',
            'client_id': '007'
            }, "secret1234567890abcdefghijklmnop", algorithm="HS256")

        lib = SW360Keycloak(self.MYURL)
        with self.assertRaises(SW360Error) as context:
            lib.is_write_token(test_token)

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Unable to analyze token: scope field missing!"))

    def test_is_write_token_invalid2(self) -> None:
        lib = SW360Keycloak(self.MYURL)
        with self.assertRaises(SW360Error) as context:
            lib.is_write_token("test_token")

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Unable to analyze token"))


if __name__ == "__main__":
    sut = Sw360TestKeycloak()
    sut.test_is_token_expired_invalid_token2()
