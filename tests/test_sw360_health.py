# -------------------------------------------------------------------------------
# Copyright (c) 2020-2022 Siemens
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


class Sw360TestHealth(unittest.TestCase):
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
    def test_get_health_status(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/health/",
            body='{"status": "UP"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        status = lib.get_health_status()
        self.assertIsNotNone(status)
        self.assertTrue("status" in status)


if __name__ == "__main__":
    unittest.main()
