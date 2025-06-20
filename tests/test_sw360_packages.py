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
from typing import Any

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error  # noqa: E402


class Sw360TestPackages(unittest.TestCase):
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

    def _my_matcher(self) -> Any:
        """
        Helper method to display the JSON parameters of a REST call.
        """
        def display_json_params(request_body: Any) -> bool:
            print("MyMatcher:'" + request_body + "'")
            return True

        return display_json_params

    @responses.activate
    def test_get_get_packages(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages/123",
            body='{"name": "Tethys.Logging", "version": "1.4.0", "purl": "pkg:nuget/Tethys.Logging@1.4.0"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        package = lib.get_package("123")
        self.assertIsNotNone(package)
        if package:  # only for mypy
            self.assertEqual("Tethys.Logging", package["name"])
            self.assertEqual("1.4.0", package["version"])

    @responses.activate
    def test_get_all_packages(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages",
            body='{"_embedded": {"sw360:packages": [{"name": "Tethys.Logging", "version": "1.3.0", "packageType": "FRAMEWORK"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_all_packages()
        self.assertIsNotNone(packages)
        if packages:  # only for mypy
            self.assertTrue(len(packages) > 0)
            self.assertEqual("Tethys.Logging", packages[0]["name"])
            self.assertEqual("1.3.0", packages[0]["version"])

    @responses.activate
    def test_get_all_packages_with_fields_and_all_details(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages?allDetails=true&purl=pkg:pypi/cli-support@2.0.0",
            body='{"_embedded": {"sw360:packages": [{"name": "Tethys.Logging", "version": "1.3.0", "packageType": "FRAMEWORK"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_all_packages(purl="pkg:pypi/cli-support@2.0.0", all_details=True)
        self.assertIsNotNone(packages)
        self.assertTrue(len(packages) > 0)
        self.assertEqual("Tethys.Logging", packages[0]["name"])
        self.assertEqual("1.3.0", packages[0]["version"])

    @responses.activate
    def test_get_all_packages_with_fields_and_all_details2(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages?allDetails=true&name=cli-support&version=2.0.0&page=2&page_entries=6&sort=name%2Cdesc",  # noqa
            body='{"_embedded": {"sw360:packages": [{"name": "Tethys.Logging", "version": "1.3.0", "packageType": "FRAMEWORK"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_all_packages(name="cli-support", version="2.0.0", all_details=True, page=2, page_size=6, sort="name,desc")  # noqa
        self.assertIsNotNone(packages)
        self.assertTrue(len(packages) > 0)
        pkgs = packages["_embedded"]["sw360:packages"]
        self.assertEqual("Tethys.Logging", pkgs[0]["name"])
        self.assertEqual("1.3.0", pkgs[0]["version"])

    @responses.activate
    def test_get_packages_by_name(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages?name=john",
            body='{"_embedded": {"sw360:packages": [{"name": "john", "version": "2.2.2", "_links": {"self": {"href": "https://my.server.com/resource/api/packages/08ddfd57636c4c47f4c879515007081f"}}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_packages_by_name("john")
        self.assertIsNotNone(packages)
        self.assertTrue(len(packages) > 0)
        self.assertEqual("john", packages[0]["name"])
        self.assertEqual("2.2.2", packages[0]["version"])

    @responses.activate
    def test_get_packages_by_packagemanager(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages?packageManager=nuget",
            body='{"_embedded": {"sw360:packages": [{"name": "john", "version": "2.2.2", "_links": {"self": {"href": "https://my.server.com/resource/api/packages/08ddfd57636c4c47f4c879515007081f"}}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_packages_by_packagemanager("nuget")
        self.assertIsNotNone(packages)
        self.assertTrue(len(packages) > 0)
        self.assertEqual("john", packages[0]["name"])
        self.assertEqual("2.2.2", packages[0]["version"])

    @responses.activate
    def test_get_packages_by_packagemanager_with_details(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/packages?packageManager=nuget&page=1&page_entries=5&sort=name%2Cdesc",
            body='{"_embedded": {"sw360:packages": [{"name": "john", "version": "2.2.2", "_links": {"self": {"href": "https://my.server.com/resource/api/packages/08ddfd57636c4c47f4c879515007081f"}}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        packages = lib.get_packages_by_packagemanager("nuget", page=1, page_size=5, sort="name,desc")
        self.assertIsNotNone(packages)
        self.assertTrue(len(packages) > 0)
        pkgs = packages["_embedded"]["sw360:packages"]
        self.assertEqual("john", pkgs[0]["name"])
        self.assertEqual("2.2.2", pkgs[0]["version"])

    @responses.activate
    def test_create_new_package(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/packages",
            json={
              # server returns complete package, here we only mock a part of it
              "name": "NewPackage",
              "version": "1.0.0",
              "_links": {
                "sw360:component": {"href": self.MYURL+'resource/api/components/9876'},
                "self": {"href": self.MYURL+'resource/api/packages/2403'}
              }
            },
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewPackage",
                "version": "1.0.0",
                "purl": "pkg:npm/NewPackage@1.0.0",
                "packageType": "LIBRARY"
              })
            ],
        )
        lib.create_new_package("NewPackage", "1.0.0", "pkg:npm/NewPackage@1.0.0", "LIBRARY")

    @responses.activate
    def test_create_new_package_already_exists(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/packages",
            json={
              "timestamp": "2024-12-13T13:44:08.349752Z", "status": 409,
              "error": "Conflict", "message": "sw360 package with name ... already exists."
            },
            status=409,
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewPackage",
                "version": "1.0.0",
                "purl": "pkg:npm/NewPackage@1.0.0",
                "packageType": "LIBRARY"
              })
            ],
        )

        with self.assertRaises(SW360Error) as context:
            lib.create_new_package("NewPackage", "1.0.0", "pkg:npm/NewPackage@1.0.0", "LIBRARY")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(409, context.exception.response.status_code)
            if context.exception.details:
                self.assertEqual(409, context.exception.details["status"])
                self.assertEqual("Conflict", context.exception.details["error"])

    @responses.activate
    def test_update_package(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/packages/123",
            body="4",
            status=202,
        )

        package = {}
        package["name"] = "NewPackage"
        package["homepageUrl"] = "https://angularJS.org"

        lib.update_package(package, "123")

    @responses.activate
    def test_update_package_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/package/123",
            body="4",
            status=403,
        )

        package = {}
        package["name"] = "NewPackage"

        with self.assertRaises(SW360Error) as context:
            lib.update_package(package, "")

        self.assertEqual("No package id provided!", context.exception.message)

    @responses.activate
    def test_update_package_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/packages/123",
            body="4",
            status=404,
        )

        package = {}
        package["name"] = "NewPackage"

        with self.assertRaises(SW360Error) as context:
            lib.update_package(package, "123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_delete_package(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/packages/123",
            body="4",
            status=200,
        )

        lib.delete_package("123")

    @responses.activate
    def test_delete_package_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.delete_package("")

        self.assertEqual("No package id provided!", context.exception.message)

    @responses.activate
    def test_delete_package_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/packages/123",
            body="4",
            status=404,
        )

        with self.assertRaises(SW360Error) as context:
            lib.delete_package("123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)


if __name__ == "__main__":
    APP = Sw360TestPackages()
    APP.test_get_packages_by_packagemanager_with_details()
