# -------------------------------------------------------------------------------
# Copyright (c) 2023 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
from typing import Any
import unittest
import warnings
from typing import Any

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error  # noqa: E402


class Sw360TestReleases(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self) -> None:
        warnings.filterwarnings(
            "ignore", category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

    def _add_login_response(self) -> None:
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

    def _my_matcher(self) -> Any:
        """
        Helper method to display the JSON parameters of a REST call.
        """
        def display_json_params(request_body: Any) -> bool:
            print("MyMatcher:'" + request_body + "'")
            return True

        return display_json_params

    @responses.activate
    def test_get_get_release(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/123",
            body='{"name": "Tethys.Logging", "version": "1.4.0", "releaseDate": "2018-03-04"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        release = lib.get_release("123")
        self.assertIsNotNone(release)
        if release:  # only for mypy
            self.assertEqual("Tethys.Logging", release["name"])
            self.assertEqual("1.4.0", release["version"])

    @responses.activate
    def test_get_get_release_internal_server_error(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/123",
            body='{"timestamp": "2020-12-10T07:22:06.1685Z", "status": "500", "error": "Internal Server Error", "message": "Handler dispatch failed; nested exception is java.lang.OutOfMemoryError: Metaspace"}',  # noqa
            status=500,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.get_release("123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(500, context.exception.response.status_code)
            if context.exception.details:
                self.assertEqual("500", context.exception.details["status"])
                self.assertEqual("Internal Server Error", context.exception.details["error"])

    @responses.activate
    def test_get_release_by_url(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/124",
            body='{"name": "Tethys.Logging", "version": "1.3.0", "releaseDate": "2018-03-04"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        release = lib.get_release_by_url(self.MYURL + "resource/api/releases/124")
        self.assertIsNotNone(release)
        if release:  # only for mypy
            self.assertEqual("Tethys.Logging", release["name"])
            self.assertEqual("1.3.0", release["version"])

    @responses.activate
    def test_get_all_releases(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases",
            body='{"_embedded": {"sw360:releases": [{"name": "Tethys.Logging", "version": "1.3.0", "releaseDate": "2018-03-04"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_all_releases()
        self.assertIsNotNone(releases)
        if releases:  # only for mypy
            self.assertTrue(len(releases) > 0)
            self.assertEqual("Tethys.Logging", releases[0]["name"])
            self.assertEqual("1.3.0", releases[0]["version"])

    @responses.activate
    def test_get_all_releases_all_details(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases?allDetails=true",
            body='{"_embedded": {"sw360:releases": [{"name": "Tethys.Logging", "version": "1.3.0", "releaseDate": "2018-03-04"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_all_releases("", True)
        self.assertIsNotNone(releases)
        self.assertTrue(len(releases) > 0)
        self.assertEqual("Tethys.Logging", releases[0]["name"])
        self.assertEqual("1.3.0", releases[0]["version"])

    @responses.activate
    def test_get_all_releases_with_fields(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases?fields=releaseDate",
            body='{"_embedded": {"sw360:releases": [{"name": "Tethys.Logging", "version": "1.3.0", "releaseDate": "2018-03-04"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_all_releases("releaseDate")
        self.assertIsNotNone(releases)
        self.assertTrue(len(releases) > 0)
        self.assertEqual("Tethys.Logging", releases[0]["name"])
        self.assertEqual("1.3.0", releases[0]["version"])

    @responses.activate
    def test_get_all_releases_with_fields_and_all_details(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases?allDetails=true&fields=releaseDate",
            body='{"_embedded": {"sw360:releases": [{"name": "Tethys.Logging", "version": "1.3.0", "releaseDate": "2018-03-04"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_all_releases("releaseDate", True)
        self.assertIsNotNone(releases)
        self.assertTrue(len(releases) > 0)
        self.assertEqual("Tethys.Logging", releases[0]["name"])
        self.assertEqual("1.3.0", releases[0]["version"])

    @responses.activate
    def test_get_releases_by_external_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/searchByExternalIds?nuget-id=Tethys.Logging.1.4.0",  # noqa
            body='{"_embedded": {"sw360:releases": [{"name": "Tethys.Logging", "version": "1.3.0", "externalIds": { "nuget-id": "Tethys.Logging.1.4.0" }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_releases_by_external_id("nuget-id", "Tethys.Logging.1.4.0")
        self.assertIsNotNone(releases)
        self.assertTrue(len(releases) > 0)
        self.assertEqual("Tethys.Logging", releases[0]["name"])
        self.assertEqual("1.3.0", releases[0]["version"])

    @responses.activate
    def test_get_releases_by_name(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases?name=john",
            body='{"_embedded": {"sw360:releases": [{"name": "john", "version": "2.2.2", "_links": {"self": {"href": "https://my.server.com/resource/api/releases/08ddfd57636c4c47f4c879515007081f"}}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_releases_by_name("john")
        self.assertIsNotNone(releases)
        self.assertTrue(len(releases) > 0)
        self.assertEqual("john", releases[0]["name"])
        self.assertEqual("2.2.2", releases[0]["version"])

    @responses.activate
    def test_create_new_release(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/releases",
            json={
              # server returns complete release, here we only mock a part of it
              "name": "NewComponent", "version": "1.0.0",
              "_links": {
                "sw360:component": {"href": self.MYURL+'resource/api/components/9876'},
                "self": {"href": self.MYURL+'resource/api/releases/2403'}
              }
            },
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewComponent", "version": "1.0.0",
                "componentId": "9876"
              })
            ],
        )
        lib.create_new_release("NewComponent", "1.0.0", "9876")

    @responses.activate
    def test_create_new_release_already_exists(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/releases",
            json={
              "timestamp": "2020-12-13T13:44:08.349752Z", "status": 409,
              "error": "Conflict", "message": "sw360 release with name ... already exists."
            },
            status=409,
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewComponent", "version": "1.0.0",
                "componentId": "9876"
              })
            ],
        )

        with self.assertRaises(SW360Error) as context:
            lib.create_new_release("NewComponent", "1.0.0", "9876")

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
    def test_update_release(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/releases/123",
            body="4",
            status=202,
        )

        release = {}
        release["name"] = "NewComponent"
        release["releaseDate"] = "2018-03-04"

        lib.update_release(release, "123")

    @responses.activate
    def test_update_release_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/release/123",
            body="4",
            status=403,
        )

        release = {}
        release["name"] = "NewComponent"

        with self.assertRaises(SW360Error) as context:
            lib.update_release(release, "")

        self.assertEqual("No release id provided!", context.exception.message)

    @responses.activate
    def test_update_release_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/releases/123",
            body="4",
            status=404,
        )

        release = {}
        release["name"] = "NewComponent"

        with self.assertRaises(SW360Error) as context:
            lib.update_release(release, "123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_update_release_external_id_add_fresh_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/123",  # noqa
            body='{"name": "Tethys.Logging", "version": "1.4.0", "externalIds": {"already-existing": "must-be-kept"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # add fresh id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/releases/123",
            body="4",
            match=[
              responses.matchers.json_params_matcher({"externalIds": {"already-existing": "must-be-kept", "package-url": "pkg:deb/debian/debootstrap?type=source"}})  # noqa
            ]
        )

        lib.update_release_external_id(
            "package-url",
            "pkg:deb/debian/debootstrap?type=source",
            "123")

    @responses.activate
    def test_delete_release(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/releases/123",
            body="4",
            status=200,
        )

        lib.delete_release("123")

    @responses.activate
    def test_delete_release_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.delete_release("")

        self.assertEqual("No release id provided!", context.exception.message)

    @responses.activate
    def test_delete_release_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/releases/123",
            body="4",
            status=404,
        )

        with self.assertRaises(SW360Error) as context:
            lib.delete_release("123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_get_users_of_release(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/releases/usedBy/123",  # noqa
            body='{"_embedded": {"sw360:projects": [{"name": "xxx", "version": "4.5"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN}
        )

        lib.get_users_of_release("123")


if __name__ == "__main__":
    unittest.main()
