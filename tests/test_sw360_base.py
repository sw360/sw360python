# -------------------------------------------------------------------------------
# Copyright (c) 2019-2024 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import json
import os
import sys
import time
import unittest
from unittest.mock import patch

import jwt
import requests
import responses

from sw360.base import BaseMixin
from sw360.sw360_api import session_default

sys.path.insert(1, "..")


from sw360 import SW360, SW360Error, SW360KeycloakClient  # noqa: E402


class Sw360Test(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def test_constructor(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self.assertEqual(self.MYURL, lib.url)

        expected_header = {"Authorization": "Token " + self.MYTOKEN}
        self.assertEqual(expected_header, lib.api_headers)

        lib = SW360(self.MYURL, self.MYTOKEN, True)
        self.assertEqual(self.MYURL, lib.url)

        expected_header = {"Authorization": "Bearer " + self.MYTOKEN}
        self.assertEqual(expected_header, lib.api_headers)

        # check for trailing slash
        lib = SW360("https://my.server.com", self.MYTOKEN, False)
        self.assertEqual(self.MYURL, lib.url)

    def _make_token(self, valid_for_seconds: int, scope: str = "READ profile email") -> str:
        signing_key = "test-signing-key-that-is-at-least-32-bytes"
        return jwt.encode(
            {"exp": int(time.time()) + valid_for_seconds, "scope": scope},
            signing_key, algorithm="HS256")

    def test_keycloak_client_uses_credentials_instead_of_token(self) -> None:
        token = self._make_token(600)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.return_value = token
            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")

        self.assertIsInstance(lib, SW360)
        self.assertEqual(self.MYURL, lib.url)
        self.assertEqual("Bearer " + token, lib.api_headers["Authorization"])
        keycloak.get_keycloak_token.assert_called_once_with(
            "client-id", "client-secret", write_access=False)

    def test_keycloak_client_renews_token_before_expiry(self) -> None:
        initial_token = self._make_token(600)
        expiring_token = self._make_token(30)
        fresh_token = self._make_token(600)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [initial_token, fresh_token]

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            self.assertEqual("Bearer " + initial_token, lib.api_headers["Authorization"])

            # simulate that the cached token is now close to expiry
            lib._keycloak_token_provider._token = expiring_token
            self.assertEqual("Bearer " + fresh_token, lib.api_headers["Authorization"])
            self.assertEqual(2, keycloak.get_keycloak_token.call_count)

    def test_keycloak_client_keeps_token_that_is_still_valid(self) -> None:
        token = self._make_token(600)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.return_value = token

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            for _ in range(3):
                self.assertEqual("Bearer " + token, lib.api_headers["Authorization"])

            self.assertEqual(1, keycloak.get_keycloak_token.call_count)

    def test_keycloak_client_honours_refresh_buffer(self) -> None:
        initial_token = self._make_token(600)
        fresh_token = self._make_token(1200)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [initial_token, fresh_token]

            # a token valid for 600s is renewed when the buffer is larger
            lib = SW360KeycloakClient(
                self.MYURL, "client-id", "client-secret", refresh_before_seconds=900)
            self.assertEqual("Bearer " + fresh_token, lib.api_headers["Authorization"])

    def test_keycloak_client_requests_write_access(self) -> None:
        token = self._make_token(600, scope="READ WRITE profile email")

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.return_value = token
            SW360KeycloakClient(self.MYURL, "client-id", "client-secret", write_access=True)

        keycloak.get_keycloak_token.assert_called_once_with(
            "client-id", "client-secret", write_access=True)

    def test_keycloak_client_reports_missing_token(self) -> None:
        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak_class.return_value.get_keycloak_token.return_value = None
            with self.assertRaises(SW360Error) as context:
                SW360KeycloakClient(self.MYURL, "client-id", "client-secret")

        self.assertEqual("Unable to obtain token from Keycloak", context.exception.message)

    def test_keycloak_client_reports_token_that_cannot_be_analyzed(self) -> None:
        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [self._make_token(600), "not-a-jwt"]

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            lib._keycloak_token_provider._token = "not-a-jwt"
            with self.assertRaises(SW360Error) as context:
                lib.current_token

        self.assertTrue(context.exception.message.startswith("Unable to analyze token:"))

    def test_keycloak_client_uses_own_session(self) -> None:
        token = self._make_token(600)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak_class.return_value.get_keycloak_token.return_value = token
            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")

        self.assertIsNot(lib.session, session_default)
        assert lib.session is not None
        prepared = lib.session.prepare_request(requests.Request("GET", self.MYURL))
        self.assertEqual("Bearer " + token, prepared.headers["Authorization"])

    def test_keycloak_client_current_token(self) -> None:
        initial_token = self._make_token(600)
        expiring_token = self._make_token(30)
        fresh_token = self._make_token(600)

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [initial_token, fresh_token]

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            self.assertEqual(initial_token, lib.current_token)

            lib._keycloak_token_provider._token = expiring_token
            self.assertEqual(fresh_token, lib.current_token)

    @responses.activate
    def test_keycloak_client_sends_renewed_token(self) -> None:
        initial_token = self._make_token(600)
        expiring_token = self._make_token(30)
        fresh_token = self._make_token(600)
        url = self.MYURL + "resource/api/releases/123"

        responses.add(responses.GET, url, body="{}", status=200,
                      content_type="application/json")

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [initial_token, fresh_token]

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            lib._keycloak_token_provider._token = expiring_token
            lib.api_get(url)

        self.assertEqual("Bearer " + fresh_token,
                         responses.calls[0].request.headers["Authorization"])

    @responses.activate
    def test_keycloak_client_sends_renewed_token_without_session(self) -> None:
        initial_token = self._make_token(600)
        expiring_token = self._make_token(30)
        fresh_token = self._make_token(600)
        url = self.MYURL + "resource/api/releases/123"

        responses.add(responses.GET, url, body="{}", status=200,
                      content_type="application/json")

        with patch("sw360.sw360_api.SW360Keycloak") as keycloak_class:
            keycloak = keycloak_class.return_value
            keycloak.get_keycloak_token.side_effect = [initial_token, fresh_token]

            lib = SW360KeycloakClient(self.MYURL, "client-id", "client-secret")
            lib.force_no_session = True
            lib._keycloak_token_provider._token = expiring_token
            lib.api_get(url)

        self.assertEqual("Bearer " + fresh_token,
                         responses.calls[0].request.headers["Authorization"])

    def test_BaseMixin_constructor(self) -> None:
        lib = BaseMixin(self.MYURL, self.MYTOKEN, False)
        self.assertEqual(self.MYURL, lib.url)

        expected_header = {"Authorization": "Token " + self.MYTOKEN}
        self.assertEqual(expected_header, lib.api_headers)

        lib = BaseMixin(self.MYURL, self.MYTOKEN, True)
        self.assertEqual(self.MYURL, lib.url)

        expected_header = {"Authorization": "Bearer " + self.MYTOKEN}
        self.assertEqual(expected_header, lib.api_headers)

        # check for trailing slash
        lib = BaseMixin("https://my.server.com", self.MYTOKEN, False)
        self.assertEqual(self.MYURL, lib.url)

    @responses.activate
    def test_login(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

    # def test_login_failed_invalid_url(self) -> None:
    #     lib = SW360(self.MYURL, self.MYTOKEN, False)

    #     have_backup = False
    #     if "SW360ProductionToken" in os.environ:
    #         have_backup = True
    #         backup = os.environ["SW360ProductionToken"]
    #         os.environ["SW360ProductionToken"] = ""

    #     with self.assertRaises(SW360Error) as context:
    #         lib.login_api()

    #     self.assertTrue(context.exception.message.startswith(self.ERROR_MSG_NO_LOGIN))

    #     if have_backup:
    #         os.environ["SW360ProductionToken"] = backup

    @responses.activate
    def test_login_failed_not_authorized(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'not_authorized'}",
            status=401,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.login_api()

        self.assertEqual(self.ERROR_MSG_NO_LOGIN, context.exception.message)

    @responses.activate
    def test_login_failed_forbidden(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'failed'}",
            status=403,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        with self.assertRaises(SW360Error) as context:
            lib.login_api()

        self.assertEqual(self.ERROR_MSG_NO_LOGIN, context.exception.message)

    def get_logged_in_lib(self) -> SW360:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        # lib.force_no_session = True

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        return lib

    @responses.activate
    def test_dump_rest_call_to_file(self) -> None:
        FILENAME = "delete_me.txt"
        if os.path.isfile(FILENAME):
            os.remove(FILENAME)

        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = False

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123X",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        lib.api_get_raw(self.MYURL + "resource/api/projects/123X")

    @responses.activate
    def test_api_get_no_content_no_session(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123",
            # body must be empty!
            status=204,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        rx = lib.get_project("123")
        self.assertIsNone(rx)

    @responses.activate
    def test_api_get_no_content(self) -> None:
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123X",
            # body must be empty!
            status=204,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        result = lib.api_get(self.MYURL + "resource/api/projects/123X")
        self.assertIsNone(result)

    @responses.activate
    def test_api_get_raw_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False, None)
        lib.force_no_session = False

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123X",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.api_get_raw(self.MYURL + "resource/api/projects/123X")

        self.assertEqual("login_api needs to be called first", context.exception.message)

    @responses.activate
    def test_api_get_raw(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123X",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        p_raw = lib.api_get_raw(self.MYURL + "resource/api/projects/123X")
        p = json.loads(p_raw)
        self.assertEqual("My Testproject", p["name"])

    @responses.activate
    def test_api_get_raw_error(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123456X",
            body='{"timestamp":"2020-11-13T17:39:28.689358Z","status":404,"error":"Not Found","message":"Requested Project Not Found"}', # noqa
            status=404,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.api_get_raw(self.MYURL + "resource/api/projects/123456X")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)
            if context.exception.details:
                self.assertEqual("Not Found", context.exception.details["error"])
                self.assertEqual("Requested Project Not Found", context.exception.details["message"])

    @responses.activate
    def test_api_get_raw_error_string(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/projects/123456X",
            body='Error-String',
            status=404,
            content_type="text/plain",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.api_get_raw(self.MYURL + "resource/api/projects/123456X")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)
            self.assertEqual("Error-String", context.exception.response.text)

    @responses.activate
    def test_login_server_not_responding(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body='{"error": "Internal Server Error", "message": "An unexpected error occurred on the server."}',
            status=500,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.login_api()

        self.assertEqual(self.ERROR_MSG_NO_LOGIN, context.exception.message)

    @responses.activate
    def test_api_post_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False, None)
        lib.force_no_session = False

        with self.assertRaises(SW360Error) as context:
            lib.api_post(self.MYURL + "resource/api/projects/123X")

        self.assertEqual("login_api needs to be called first", context.exception.message)

    @responses.activate
    def test_api_post_multipart_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False, None)
        lib.force_no_session = False

        with self.assertRaises(SW360Error) as context:
            lib.api_post_multipart(self.MYURL + "resource/api/projects/123X")

        self.assertEqual("login_api needs to be called first", context.exception.message)

    @responses.activate
    def test_api_patch_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False, None)
        lib.force_no_session = False

        with self.assertRaises(SW360Error) as context:
            lib.api_patch(self.MYURL + "resource/api/projects/123X")

        self.assertEqual("login_api needs to be called first", context.exception.message)

    @responses.activate
    def test_api_delete_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False, None)
        lib.force_no_session = False

        with self.assertRaises(SW360Error) as context:
            lib.api_delete(self.MYURL + "resource/api/projects/123X")

        self.assertEqual("login_api needs to be called first", context.exception.message)


if __name__ == "__main__":
    APP = Sw360Test()
    APP.test_api_post_multipart_not_logged_in()
