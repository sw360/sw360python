# -------------------------------------------------------------------------------
# Copyright (c) 2020-2023 Siemens
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

from sw360 import SW360, SW360Error

sys.path.insert(1, "..")


class Sw360TestLicenses(unittest.TestCase):
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
    def test_get_all_licenses(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/licenses",
            body='{"_embedded": {\
                    "sw360:licenses": [\
                        {"checked": true,\
                         "fullName": "BSD Zero Clause License",\
                         "_links": {\
                           "self": {"href": "https://sw360.siemens.com/resource/api/licenses/0BSD"}\
                         }},\
                         {"checked": true,\
                          "fullName": "Attribution Assurance License",\
                          "_links": {\
                            "self": {"href": "https://sw360.siemens.com/resource/api/licenses/AAL"}\
                          }}]},\
                         "_links": {"curies": \
                            [{"href": "https://sw360.siemens.com/resource/docs/{rel}.html",\
                           "name": "sw360", "templated": true}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        licenses = lib.get_all_licenses()
        self.assertIsNotNone(licenses)
        self.assertTrue(len(licenses) > 0)
        self.assertEqual("BSD Zero Clause License", licenses[0]["fullName"])

    @responses.activate
    def test_get_all_licenses_none(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/licenses",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        licenses = lib.get_all_licenses()
        self.assertIsNone(licenses)

    @responses.activate
    def test_get_license(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/licenses/Apache-2.0",
            body='{"externalIds": { "SPDX-License-Identifier": "Apache-2.0" },\
                    "text": "Apache License Version 2.0, ...",\
                    "checked": "True",\
                    "shortName": "Apache-2.0",\
                    "fullName": "Apache License 2.0",\
                    "_links": { "self": {\
                         "href": "https://sw360.siemens.com/resource/api/licenses/Apache-2.0" } }}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        license = lib.get_license("Apache-2.0")
        self.assertIsNotNone(license)
        self.assertEqual("True", license["checked"])
        self.assertEqual("Apache-2.0", license["shortName"])
        self.assertEqual("Apache License 2.0", license["fullName"])

    @responses.activate
    def test_create_new_license(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=f"{self.MYURL}resource/api/licenses",
            status=201,
            json={
                # server returns full license, here we only mock a part of it
                'shortName': 'LGPL-2.0-only',
                'fullName': 'GNU Library General Public License v2 only',
                'checked': True,
                '_links': {
                    'self': {
                        'href': f"{self.MYURL}resource/api/licenses/LGPL-2.0-only"
                    }
                }
            },
            match=[responses.matchers.json_params_matcher({
                "shortName": "LGPL-2.0-only",
                "fullName": "GNU Library General Public License v2 only",
                "checked": True,
                "text": ""})]
        )
        lib.create_new_license(
            shortName="LGPL-2.0-only",
            fullName="GNU Library General Public License v2 only",
            text="",
            checked=True,
        )

    @responses.activate
    def test_create_new_license_fail(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=f"{self.MYURL}resource/api/licenses",
            status=403,
            json={
                # server returns full license, here we only mock a part of it
                'shortName': 'LGPL-2.0-only',
                'fullName': 'GNU Library General Public License v2 only',
                'checked': True,
                '_links': {
                    'self': {
                        'href': f"{self.MYURL}resource/api/licenses/LGPL-2.0-only"
                    }
                }
            },
            match=[responses.matchers.json_params_matcher({
                "shortName": "LGPL-2.0-only",
                "fullName": "GNU Library General Public License v2 only",
                "checked": True,
                "text": ""})]
        )

        with self.assertRaises(SW360Error) as context:
            lib.create_new_license(
                shortName="LGPL-2.0-only",
                fullName="GNU Library General Public License v2 only",
                text="",
                checked=True,
            )
        self.assertEqual(403, context.exception.response.status_code)

    @responses.activate
    def test_delete_license(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/licenses/LGPL-2.0-only",
            status=201)

        lib.delete_license("LGPL-2.0-only")


if __name__ == "__main__":
    unittest.main()
