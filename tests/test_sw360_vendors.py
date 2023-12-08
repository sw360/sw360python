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

from sw360 import SW360, SW360Error  # noqa: E402


class Sw360TestVendors(unittest.TestCase):
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
    def test_get_all_vendors_not_yet_implemented(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vendors",  # noqa
            body='{"_embedded": {"sw360:vendors": [\
            { "url": "http://no.data.from.source/",\
            "shortName": "Triangle, Inc.", "fullName": "Triangle, Inc.",\
            "_links": {"self": {\
                "href": "https://sw360.siemens.com/resource/api/vendors/12345"\
            }}},\
            {"url": "http://me.com",\
            "shortName": "Me", "fullName": "Me, Inc.",\
            "_links": {"self": {\
                "href": "https://sw360.siemens.com/resource/api/vendors/99999"\
            }}}]},\
            "_links": {"curies": [ {\
                "href": "https://sw360.siemens.com/resource/docs/{rel}.html",\
                "name": "sw360", "templated": "True"\
            }]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.api_get(self.MYURL + "resource/api/vendors")
        self.assertIsNotNone(data)
        self.assertTrue("_embedded" in data)
        self.assertTrue("sw360:vendors" in data["_embedded"])
        vlist = data["_embedded"]["sw360:vendors"]
        self.assertEqual(2, len(vlist))
        self.assertEqual("Triangle, Inc.", vlist[0]["shortName"])
        self.assertEqual("Me", vlist[1]["shortName"])

    @responses.activate
    def test_get_vendor(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vendors/12345",
            body='{"url": "http://no.data.from.source/",\
              "shortName": "Triangle, Inc.",\
              "fullName": "Triangle, Inc.",\
              "_links": { "self": {\
              "href": "https://my.server.com/resource/api/vendors/12345"}}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        vendor = lib.get_vendor("12345")
        self.assertIsNotNone(vendor)
        self.assertEqual("Triangle, Inc.", vendor["shortName"])

    @responses.activate
    def test_get_all_vendors(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vendors",
            body='{"_embedded" : {\
                "sw360:vendors" : [{\
                    "fullName": "Premium Software",\
                    "_links": { "self": {\
                             "href": "https://my.server.com/resource/api/vendors/006"}}}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        vendors = lib.get_all_vendors()
        self.assertIsNotNone(vendors)
        self.assertEqual(1, len(vendors))
        self.assertEqual("Premium Software", vendors[0]["fullName"])

    @responses.activate
    def test_get_all_vendors_no_result(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/vendors",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        vendors = lib.get_all_vendors()
        self.assertIsNone(vendors)

    @responses.activate
    def test_create_new_vendor(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/vendors",
            body='{"status": "success"}',
            status=201,
            match=[
              responses.matchers.json_params_matcher({
                  "url": "https://github.com/tngraf",
                  "shortName": "tngraf",
                  "fullName": "Thomas Graf"
                  })
            ],
            content_type="application/hal+json"
        )

        vendor = {}
        vendor["url"] = "https://github.com/tngraf"
        vendor["shortName"] = "tngraf"
        vendor["fullName"] = "Thomas Graf"

        lib.create_new_vendor(vendor)

    @responses.activate
    def test_create_new_vendor_fail(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/vendors",
            body='{"status": "success"}',
            status=403,
            match=[
              responses.matchers.json_params_matcher({
                  "url": "https://github.com/tngraf",
                  "shortName": "tngraf",
                  "fullName": "Thomas Graf"
                  })
            ],
            content_type="application/hal+json"
        )

        vendor = {}
        vendor["url"] = "https://github.com/tngraf"
        vendor["shortName"] = "tngraf"
        vendor["fullName"] = "Thomas Graf"

        with self.assertRaises(SW360Error) as context:
            lib.create_new_vendor(vendor)

        self.assertEqual(403, context.exception.response.status_code)

    @responses.activate
    def test_update_vendor_no_id(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        vendor = {}
        vendor["shortName"] = "xxx"

        with self.assertRaises(SW360Error) as context:
            lib.update_vendor(vendor, None)

        self.assertEqual("No vendor id provided!", context.exception.message)

    @responses.activate
    def test_update_vendor(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/vendors/112233",
            body="4",
            status=201,
            match=[
              responses.matchers.json_params_matcher({
                  "shortName": "xxx",
                  })
            ],
        )

        vendor = {}
        vendor["shortName"] = "xxx"
        lib.update_vendor(vendor, "112233")

    @responses.activate
    def test_update_vendor_fail(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/vendors/112233",
            body="4",
            status=403,
        )

        vendor = {}
        vendor["shortName"] = "xxx"

        with self.assertRaises(SW360Error) as context:
            lib.update_vendor(vendor, "112233")

        self.assertEqual(403, context.exception.response.status_code)

    @responses.activate
    def test_delete_vendor_no_id(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.delete_vendor(None)

        self.assertEqual("No vendor id provided!", context.exception.message)

    @responses.activate
    def test_delete_vendor(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/vendors/123",
            body="4",
            status=200,
        )

        lib.delete_vendor("123")

    @responses.activate
    def test_delete_vendor_fail(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/vendors/123",
            body="4",
            status=405,
        )

        with self.assertRaises(SW360Error) as context:
            lib.delete_vendor("123")

        self.assertEqual(405, context.exception.response.status_code)


if __name__ == "__main__":
    unittest.main()
