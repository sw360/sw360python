﻿# -------------------------------------------------------------------------------
# Copyright (c) 2020-2025 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import os
import sys
import unittest
import warnings
from typing import Any

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error  # noqa: E402


class Sw360TestComponents(unittest.TestCase):
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
    def test_get_all_components(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components()
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])

    @responses.activate
    def test_get_all_components_no_result(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components",  # noqa
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components()
        self.assertEqual([], components)

    @responses.activate
    def test_get_all_components_with_fields(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?fields=ownerCountry",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components("ownerCountry")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])
        self.assertEqual("DE", components[0]["ownerCountry"])

    @responses.activate
    def test_get_all_components_with_fields_and_paging(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)
        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?fields=ownerCountry&page=1&page_entries=2",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.get_all_components("ownerCountry", 1, 2)
        components = data["_embedded"]["sw360:components"]
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])
        self.assertEqual("DE", components[0]["ownerCountry"])

    @responses.activate
    def test_get_all_components_with_all_details(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?allDetails=true",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components(all_details=True)
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])
        self.assertEqual("DE", components[0]["ownerCountry"])

    @responses.activate
    def test_get_all_components_with_all_details_and_sorting(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?allDetails=true&sort=name%2Cdesc",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components(all_details=True, sort="name,desc")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])
        self.assertEqual("DE", components[0]["ownerCountry"])

    @responses.activate
    def test_get_all_components_invalid_reply(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components",  # noqa
            body='{"_xxembedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components(all_details=True, sort="name,desc")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) == 0)

    @responses.activate
    def test_get_all_components_invalid_reply2(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components",  # noqa
            body='{"_embedded": {"xxsw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_all_components(all_details=True, sort="name,desc")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) == 0)

    @responses.activate
    def test_get_all_components_by_type(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?type=OSS",
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_type("OSS")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])
        self.assertEqual("OSS", components[0]["componentType"])

    @responses.activate
    def test_get_all_components_by_type_no_result(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?type=OSS",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_type("OSS")
        self.assertEqual([], components)

    @responses.activate
    def test_get_all_components_by_type_invalid_reply(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?type=OSS",
            body='{"_xxembedded": {"sw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_type("OSS")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) == 0)

    @responses.activate
    def test_get_all_components_by_type_invalid_reply2(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?type=OSS",
            body='{"_embedded": {"xxsw360:components": [{"name": "Tethys.Logging", "ownerCountry": "DE", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_type("OSS")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) == 0)

    @responses.activate
    def test_get_component(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/components/123",
            body='{"name": "Tethys.Logging"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        comp = lib.get_component("123")
        if comp:  # only for mypy
            self.assertEqual("Tethys.Logging", comp["name"])

    @responses.activate
    def test_get_component_by_url(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/123",
            body='{"name": "Tethys.Logging1"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        comp = lib.get_component_by_url(self.MYURL + "resource/api/components/123")
        if comp:  # only for mypy
            self.assertEqual("Tethys.Logging1", comp["name"])

    @responses.activate
    def test_get_component_by_name(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components?name=MyComponent",
            body='{"name": "MyComponent"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        comp = lib.get_component_by_name("MyComponent")
        if comp:  # only for mypy
            self.assertEqual("MyComponent", comp["name"])

    @responses.activate
    def test_get_components_by_external_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/searchByExternalIds?package-url=pkg:nuget/Tethys.Logging",  # noqa
            body='{"_embedded":{"sw360:components" :[{"name": "Tethys.Logging", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_external_id("package-url", "pkg:nuget/Tethys.Logging")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])

    @responses.activate
    def test_get_components_by_external_id_full_answer(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/searchByExternalIds?package-url=pkg:nuget/Tethys.Logging",  # noqa
            body='{"_embedded": {"sw360:components": [{"name": "Tethys.Logging", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_external_id("package-url", "pkg:nuget/Tethys.Logging")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) > 0)
        self.assertEqual("Tethys.Logging", components[0]["name"])

    @responses.activate
    def test_get_components_by_external_id_invalid_answer(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/searchByExternalIds?package-url=pkg:nuget/Tethys.Logging",  # noqa
            body='{"_xxembedded":{"sw360:components" :[{"name": "Tethys.Logging", "componentType": "OSS", "externalIds": {"package-url": "pkg:nuget/Tethys.Logging"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_components_by_external_id("package-url", "pkg:nuget/Tethys.Logging")
        self.assertIsNotNone(components)
        self.assertTrue(len(components) == 0)

    @responses.activate
    def test_update_component_external_id_add_fresh_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS", "externalIds": {"already-existing": "must-be-kept"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # add fresh id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",
            body="4",
            match=[
              responses.matchers.json_params_matcher({"externalIds": {"already-existing": "must-be-kept", "package-url": "pkg:deb/debian/debootstrap?type=source"}})  # noqa
            ]
        )

        lib.update_component_external_id(
            "package-url",
            "pkg:deb/debian/debootstrap?type=source",
            "bc75c910ca9866886cb4d7b3a301061f")

    @responses.activate
    def test_update_component_external_id_no_overwrite(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS", "externalIds": {"package-url": "pkg:deb/debian/debootstrap?type=source"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # assure that existing id is not overwritten by default
        lib.update_component_external_id(
            "package-url",
            "new-one",
            "bc75c910ca9866886cb4d7b3a301061f")

    @responses.activate
    def test_update_component_external_id_overwrite(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS", "externalIds": {"package-url": "pkg:deb/debian/debootstrap?type=source"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # assure that existing id is overwritten in overwrite mode
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",
            body="4",
            match=[
              responses.matchers.json_params_matcher({"externalIds": {"package-url": "new-one"}})
            ]
        )

        lib.update_component_external_id(
            "package-url",
            "new-one",
            "bc75c910ca9866886cb4d7b3a301061f",
            update_mode="overwrite")

    @responses.activate
    def test_update_component_external_id_delete(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS", "externalIds": {"package-url": "pkg:deb/debian/debootstrap?type=source"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # delete existing id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",
            body="4",
            match=[
              responses.matchers.json_params_matcher({"externalIds": {}})
            ]
        )

        lib.update_component_external_id(
            "package-url",
            "",
            "bc75c910ca9866886cb4d7b3a301061f",
            update_mode="delete")

    @responses.activate
    def test_update_component_external_id_no_exist(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS", "externalIds": {"already-existing": "must-be-kept"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # assure patch request doesn't happen if deleting non-existent id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",
            body="4",
            match=[
                responses.matchers.json_params_matcher(
                    {
                        "externalIds": {"xxx": "pkg:deb/debian/debootstrap?type=source"}
                    }
                )
            ]
        )

        lib.update_component_external_id(
            "package-url",
            "",
            "bc75c910ca9866886cb4d7b3a301061f",
            update_mode="delete")

    @responses.activate
    def test_update_component_external_id_no_extids_yet(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # add fresh id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/bc75c910ca9866886cb4d7b3a301061f",
            body="4",
            match=[
              responses.matchers.json_params_matcher({"externalIds": {"package-url": "pkg:deb/debian/debootstrap?type=source"}})  # noqa
            ]
        )

        lib.update_component_external_id(
            "package-url",
            "pkg:deb/debian/debootstrap?type=source",
            "bc75c910ca9866886cb4d7b3a301061f")

    @responses.activate
    def test_create_new_component(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/components",
            json={
                # server returns complete component, here we only mock a part of it
                'name': 'NewComponent',
                '_links': {
                    'self': {
                        'href': self.MYURL+'resource/api/components/2402'
                    }
                }
            },
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewComponent",
                "componentType": "OSS",
                "description": "Illustrative example component",
                "homepage": "https://www.github.com/NewComponent"
              })
            ]
        )
        lib.create_new_component(
            name="NewComponent",
            component_type="OSS",
            description="Illustrative example component",
            homepage="https://www.github.com/NewComponent"
        )

    @responses.activate
    def test_create_new_component_fail(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/components",
            json={
                "timestamp": "2020-12-12T19:15:18.702505Z",
                "error": "Conflict",
                "message": "sw360 component with name \'NewComponent\' already exists."
            },
            status=409,
            match=[
              responses.matchers.json_params_matcher({
                "name": "NewComponent",
                "componentType": "OSS",
                "description": "Illustrative example component",
                "homepage": "https://www.github.com/NewComponent"
              })
            ]
        )

        with self.assertRaises(SW360Error) as context:
            lib.create_new_component(
                name="NewComponent",
                component_type="OSS",
                description="Illustrative example component",
                homepage="https://www.github.com/NewComponent"
            )

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(409, context.exception.response.status_code)

    @responses.activate
    def test_update_component_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        comp = {}
        comp["name"] = "NewComponent"

        with self.assertRaises(SW360Error) as context:
            lib.update_component(comp, "")

        self.assertEqual("No component id provided!", context.exception.message)

    @responses.activate
    def test_update_component_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/components/123",
            body="4",
            status=403,
        )

        comp = {}
        comp["name"] = "NewComponent"

        with self.assertRaises(SW360Error) as context:
            lib.update_component(comp, "123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(403, context.exception.response.status_code)

    @responses.activate
    def test_delete_component(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/components/123",
            body='{\n  "resourceId" : "468abcd6e7f849199d9323c9a16b2776",\n  "status" : 200\n}',
            status=200,
        )

        lib.delete_component("123")

    @responses.activate
    def test_delete_component_no_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.delete_component("")

        self.assertEqual("No component id provided!", context.exception.message)

    @responses.activate
    def test_delete_component_failed(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/components/123",
            body="4",
            status=404,
        )

        with self.assertRaises(SW360Error) as context:
            lib.delete_component("123")

        if not context.exception:
            self.assertTrue(False, "no exception")

        if context.exception.response is None:
            self.assertTrue(False, "no response")
        else:
            self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_get_users_of_component(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/components/usedBy/123",  # noqa
            body='{"name": "debootstrap", "componentType": "OSS"}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN}
        )

        lib.get_users_of_component("123")

    def xtest_get_component_real(self) -> None:
        """
        Only for debugging...
        """
        lib = SW360("https://sw360.siemens.com", os.environ["SW360ProductionToken"], False)
        lib.login_api()
        # c = lib.get_component("eaba2f0416e000e8ca5b2ccb4400633e")
        # c = lib.get_components_by_external_id( "package-url", "pkg:nuget/Tethys.Logging")
        c = lib.api_get("https://my.server.com/resource/api/components/searchByExternalIds?package-url=pkg:nuget/Tethys.Logging")  # noqa
        print(c)

    @responses.activate
    def test_get_recent_components(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/recentComponents",
            body='''{
                "_embedded": {
                    "sw360:components": [
                        {
                            "id": "ff6f1b5b212b4f93b306e2cceca4f64d",
                            "name": "intl-listformat",
                            "description": "n/a",
                            "componentType": "OSS",
                            "visbility": "EVERYONE",
                            "mainLicenseIds": [],
                            "_links": {
                                "self": {
                                "href": "https://my.server.com/resource/api/components/ff"
                                }
                            }
                        },
                        {
                            "id": "f916b35d6c864014bd8823c45615aeab",
                            "name": "fields-metadata-plugin",
                            "description": "n/a",
                            "componentType": "OSS",
                            "visbility": "EVERYONE",
                            "mainLicenseIds": [],
                            "_links": {
                                "self": {
                                "href": "https://my.server.com/resource/api/components/f9"
                                }
                            }
                        }
                    ]
                },
                "_links": {
                    "curies": [
                        {
                            "href": "https://my.server.com/resource/docs/{rel}.html",
                            "name": "sw360",
                            "templated": true
                        }
                    ]
                }
            }''',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        components = lib.get_recent_components()
        self.assertIsNotNone(components)
        if components:
            self.assertEqual(2, len(components))
            self.assertEqual("intl-listformat", components[0]["name"])
            self.assertEqual("OSS", components[0]["componentType"])


if __name__ == "__main__":
    x = Sw360TestComponents()
    x.test_get_all_components_by_type()
