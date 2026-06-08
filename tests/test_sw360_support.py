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

from sw360 import SW360  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
