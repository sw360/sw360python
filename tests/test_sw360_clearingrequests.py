# -------------------------------------------------------------------------------
# Copyright (c) 2021 Siemens
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

sys.path.insert(1, "..")

from sw360 import SW360  # noqa: E402


class Sw360TestClearingRequests(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self):
        warnings.filterwarnings(
            "ignore", category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

    def _add_login_response(self):
        """
        Add the response for a successfull login.
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
    def test_get_clearing_request(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/clearingrequest/12345",
            body='{"id": "12345",\
              "requestedClearingDate": "2021-09-04",\
              "projectId": "007",\
              "clearingState": "NEW"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        vendor = lib.get_clearing_request("12345")
        self.assertIsNotNone(vendor)
        self.assertEqual("2021-09-04", vendor["requestedClearingDate"])

    @responses.activate
    def test_get_clearing_request_for_project(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/clearingrequest/project/12345",
            body='{"id": "12345",\
              "requestedClearingDate": "2021-09-04",\
              "projectId": "007",\
              "clearingState": "NEW"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        vendor = lib.get_clearing_request_for_project("12345")
        self.assertIsNotNone(vendor)
        self.assertEqual("2021-09-04", vendor["requestedClearingDate"])


if __name__ == "__main__":
    unittest.main()
