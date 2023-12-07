# -------------------------------------------------------------------------------
# Copyright (c) 2020 Siemens
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


class Sw360TestVulnerabilities(unittest.TestCase):
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
    def test_get_all_vulnerabilities(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vulnerabilities",
            body='{"_embedded" : {"sw360:vulnerabilities" : [\
                  {"externalId" : "123", "title" : "Title of vulnerability 12345",\
                  "_links" : {"self" : {"href" : "https://sw360.org/api/vulnerabilities/123" } } },\
                  {"externalId" : "7543", "title" : "Title of vulnerability 7854",\
                  "_links" : {"self" : {"href" : "https://sw360.org/api/vulnerabilities/7543" } } }\
                  ]},\
                  "_links" : {"curies" : [ {"href" : "https://sw360.org/docs/{rel}.html",\
                  "name" : "sw360", "templated" : true } ]  } }',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.get_all_vulnerabilities()
        self.assertIsNotNone(data)
        self.assertTrue("_embedded" in data)
        self.assertTrue("sw360:vulnerabilities" in data["_embedded"])
        vlist = data["_embedded"]["sw360:vulnerabilities"]
        self.assertEqual(2, len(vlist))
        self.assertEqual("Title of vulnerability 12345", vlist[0]["title"])

    @responses.activate
    def test_get_vulnerability(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vulnerabilities/47936",  # noqa
            body='{"lastUpdateDate": "2020-12-03 01:14:26",\
                 "externalId": "47936",\
                 "title": "CentOS 7 - bind Denial of Service Vulnerability",\
                 "description": "A flaw was found in ...",\
                 "_links": {"self": {"href": "https://sw360.siemens.com/resource/api/vulnerabilities/47936"}}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        v = lib.get_vulnerability("47936")
        self.assertIsNotNone(v)
        self.assertEqual("47936", v["externalId"])


if __name__ == "__main__":
    unittest.main()
