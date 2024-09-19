# -------------------------------------------------------------------------------
# Copyright (c) 2024 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
import unittest
import warnings

import responses

from sw360 import SW360Error, SW360OAuth2

sys.path.insert(1, "..")


class Sw360TestOauth2(unittest.TestCase):
    MYURL = "https://my.server.com/"
    USER = "myuser"
    PASSWORD = "secretpassword"

    def setUp(self) -> None:
        warnings.filterwarnings(
            "ignore", category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

    @responses.activate
    def test_constructor(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)
        self.assertEqual(lib.url, self.MYURL)
        self.assertEqual(lib._client_id, "myclientid")
        self.assertEqual(lib._client_secret, "myclientsecret")

    @responses.activate
    def test_constructor_no_connection(self) -> None:
        with self.assertRaises(SW360Error) as context:
            SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Unable to connect to oauth2 service: "))

    @responses.activate
    def test_create_client_read(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)
        responses.add(
            responses.POST,
            url=f"{self.MYURL}authorization/client-management",
            status=201,
            json={
                'something': 'something',
            },
            # match=[responses.matchers.json_params_matcher({
            #    "description": "mydescription",
            #    "authorities": ["BASIC"],
            #    "scope": "[READ]",
            #    "access_token_validity": 3600,
            #    "refresh_token_validity": 3600,
            #    })]
        )

        lib.create_client("mydescription", False)

    @responses.activate
    def test_create_client_read_write(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)
        responses.add(
            responses.POST,
            url=f"{self.MYURL}authorization/client-management",
            status=201,
            json={
                'something': 'something',
            },
            # match=[responses.matchers.json_params_matcher({
            #    "description": "mydescription",
            #    "authorities": ["BASIC"],
            #    "scope": "[WRITE]",
            #    "access_token_validity": 3600,
            #    "refresh_token_validity": 3600,
            #    })]
        )

        lib.create_client("mydescription", True)

    @responses.activate
    def test_create_client_failed(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)
        with self.assertRaises(SW360Error) as context:
            lib.create_client("mydescription", False)

        if not context.exception:
            self.assertTrue(False, "no exception")

        self.assertTrue(context.exception.message.startswith("Can't create oauth client:"))

    @responses.activate
    def test_token(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/oauth/token?grant_type=password&username=myuser&password=secretpassword",
            body='{"access_token": "myaccesstoken", "refresh_token": "myrefreshtoken"}',
            status=200,
            content_type="application/json",
        )
        mytoken = lib.token
        self.assertEqual(mytoken, "myaccesstoken")

    @responses.activate
    def test_refresh_token(self) -> None:
        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/client-management",
            body='[{"client_id": "myclientid", "client_secret": "myclientsecret"}]',
            status=200,
            content_type="application/json",
        )

        lib = SW360OAuth2(self.MYURL, self.USER, self.PASSWORD)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "authorization/oauth/token?grant_type=password&username=myuser&password=secretpassword",
            body='{"access_token": "myaccesstoken", "refresh_token": "myrefreshtoken"}',
            status=200,
            content_type="application/json",
        )
        myrefreshtoken = lib.refresh_token
        self.assertEqual(myrefreshtoken, "myrefreshtoken")


if __name__ == "__main__":
    LIB = Sw360TestOauth2()
    LIB.test_constructor_no_connection()
