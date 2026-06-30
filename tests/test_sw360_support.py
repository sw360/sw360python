# -------------------------------------------------------------------------------
# Copyright (c) 2020-2026 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com
# Authors: gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
import unittest

sys.path.insert(1, "..")

from sw360 import SW360, SW360Response  # noqa: E402


class Sw360TestSupportMethods(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def test_get_id_from_href(self) -> None:
        URL = "https://sw360.siemens.com/resource/api/releases/00dc0db789f9372ed6bcfd55f100e3ce"

        lib = SW360(self.MYURL, self.MYTOKEN, False)
        actual = lib.get_id_from_href(URL)
        self.assertEqual("00dc0db789f9372ed6bcfd55f100e3ce", actual)

    def test_get_linked_id_missing_key(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {
            "_links": {
                "self": {
                    "href": "https://sw360.example.com/api/releases/abc123"
                }
            }
        }
        self.assertIsNone(lib.get_linked_id(data, "sw360:component"))

    def test_get_linked_id_multiple_links(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {
            "_links": {
                "self": {
                    "href": "https://sw360.example.com/api/releases/rel001"
                },
                "sw360:component": {
                    "href": "https://sw360.example.com/api/components/comp42"
                },
                "sw360:project": {
                    "href": "https://sw360.example.com/api/projects/proj99"
                }
            }
        }
        self.assertEqual("rel001", lib.get_linked_id(data, "self"))
        self.assertEqual("comp42", lib.get_linked_id(data, "sw360:component"))
        self.assertEqual("proj99", lib.get_linked_id(data, "project"))

    def test_get_self_id(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {
            "_links": {
                "self": {
                    "href": "https://sw360.example.com/api/releases/abc123"
                }
            }
        }
        self.assertEqual("abc123", lib.get_linked_id(data))

    def test_get_embedded_releases(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {
            "_embedded": {
                "sw360:releases": [
                    {"name": "acl", "version": "1.4"},
                    {"name": "zlib", "version": "1.2.11"}
                ]
            }
        }
        result = lib.get_embedded(data, "sw360:releases")
        self.assertEqual(2, len(result))
        self.assertEqual("zlib", result[1]["name"])

        result = lib.get_embedded(data, "releases")
        self.assertEqual(2, len(result))
        self.assertEqual("zlib", result[1]["name"])

    def test_get_embedded_missing_section(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {"name": "My Project"}
        self.assertEqual([], lib.get_embedded(data, "sw360:releases"))

    def test_get_embedded_missing_key(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        data = {
            "_embedded": {
                "sw360:components": [
                    {"name": "curl"}
                ]
            }
        }
        self.assertEqual([], lib.get_embedded(data, "sw360:releases"))


class Sw360ResponseTest(unittest.TestCase):

    def test_is_still_a_dict(self) -> None:
        resp = SW360Response({"name": "acl", "version": "1.4"})
        self.assertEqual("acl", resp["name"])
        self.assertEqual("1.4", resp["version"])
        self.assertTrue(isinstance(resp, dict))

    def test_linked_id_defaults_to_self(self) -> None:
        resp = SW360Response({
            "_links": {
                "self": {
                    "href": "https://sw360.example.com/api/releases/abc123"
                }
            }
        })
        self.assertEqual("abc123", resp.linked_id())

    def test_linked_id_with_key(self) -> None:
        resp = SW360Response({
            "_links": {
                "sw360:component": {
                    "href": "https://sw360.example.com/api/components/7b4"
                }
            }
        })
        self.assertEqual("7b4", resp.linked_id("sw360:component"))
        self.assertEqual("7b4", resp.linked_id("component"))

    def test_linked_id_missing_links(self) -> None:
        resp = SW360Response({"name": "acl"})
        self.assertIsNone(resp.linked_id())

    def test_linked_ids(self) -> None:
        resp = SW360Response({
            "_links": {
                "self": {
                    "href": "https://sw360.example.com/api/releases/abc123"
                },
                "sw360:component": {
                    "href": "https://sw360.example.com/api/components/7b4"
                }
            }
        })
        ids = resp.linked_ids()
        self.assertEqual("abc123", ids["self"])
        self.assertEqual("7b4", ids["sw360:component"])
        self.assertEqual(2, len(ids))

    def test_linked_ids_empty_when_no_links(self) -> None:
        resp = SW360Response({"name": "acl"})
        self.assertEqual({}, resp.linked_ids())

    def test_embedded_list(self) -> None:
        resp = SW360Response({
            "_embedded": {
                "sw360:releases": [
                    {"name": "acl", "version": "1.4",
                     "_links": {"self": {"href": "https://sw360.example.com/api/releases/r1"}}}
                ]
            }
        })
        result = resp.embedded_list("releases")
        self.assertEqual(1, len(result))
        self.assertEqual("acl", result[0]["name"])
        self.assertIsInstance(result[0], SW360Response)
        self.assertEqual("r1", result[0].linked_id())

    def test_embedded_list_with_prefixed_key(self) -> None:
        resp = SW360Response({
            "_embedded": {
                "sw360:releases": [
                    {"name": "acl"}
                ]
            }
        })
        self.assertEqual(1, len(resp.embedded_list("sw360:releases")))

    def test_embedded_list_empty_when_missing(self) -> None:
        resp = SW360Response({"name": "My Project"})
        self.assertEqual([], resp.embedded_list("releases"))

    def test_embedded_lists(self) -> None:
        resp = SW360Response({
            "_embedded": {
                "sw360:releases": [
                    {"name": "acl",
                     "_links": {"self": {"href": "https://sw360.example.com/api/releases/r1"}}}
                ],
                "sw360:attachments": [
                    {"filename": "source.tar.gz",
                     "_links": {"self": {"href": "https://sw360.example.com/api/attachments/a1"}}}
                ]
            }
        })
        lists = resp.embedded_lists()
        self.assertEqual(2, len(lists))
        self.assertIn("sw360:releases", lists)
        self.assertIn("sw360:attachments", lists)
        self.assertIsInstance(lists["sw360:releases"][0], SW360Response)
        self.assertEqual("r1", lists["sw360:releases"][0].linked_id())
        self.assertIsInstance(lists["sw360:attachments"][0], SW360Response)
        self.assertEqual("a1", lists["sw360:attachments"][0].linked_id())

    def test_embedded_lists_empty_when_no_embedded(self) -> None:
        resp = SW360Response({"name": "My Project"})
        self.assertEqual({}, resp.embedded_lists())


if __name__ == "__main__":
    unittest.main()
