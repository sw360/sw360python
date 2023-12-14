# -------------------------------------------------------------------------------
# Copyright (c) 2019-2020 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import json
import os
import sys
import unittest

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error  # noqa: E402


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

    def test_login_failed_invalid_url(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        have_backup = False
        if "SW360ProductionToken" in os.environ:
            have_backup = True
            backup = os.environ["SW360ProductionToken"]
            os.environ["SW360ProductionToken"] = ""

        with self.assertRaises(SW360Error) as context:
            lib.login_api()

        self.assertTrue(context.exception.message.startswith(self.ERROR_MSG_NO_LOGIN))

        if have_backup:
            os.environ["SW360ProductionToken"] = backup

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
    def test_api_get_no_content(self) -> None:
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123X",
            body='{"name": "My Testproject"}',
            status=204,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        try:
            result = lib.api_get(self.MYURL + "resource/api/projects/123X")
            self.assertIsNone(result)
        except Exception:
            self.assertIsNone(None)

    @responses.activate
    def test_api_get_raw_not_logged_in(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
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


if __name__ == "__main__":
    unittest.main()
