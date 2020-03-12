# -------------------------------------------------------------------------------
# Copyright (c) 2020-2025 Siemens
# All Rights Reserved.
# Author: gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import responses
import unittest
from tests.test_sw360obj_base import Sw360ObjTestBase, SW360_BASE_URL
from sw360 import Release


class Sw360ObjTestRelease(Sw360ObjTestBase):
    def test_repr(self):
        r = Release(release_id="123", name="TestCmp", version="1.4",
                    component_id="456", downloadurl="http://www")

        r = eval(repr(r))
        assert r.id == "123"
        assert r.name == "TestCmp"
        assert r.version == "1.4"
        self.assertEqual(str(r), "TestCmp 1.4 (123)")

        r = Release()
        r = eval(repr(r))
        assert r.id is None
        assert r.name is None
        assert r.version is None

    @responses.activate
    def test_get_release(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/123",
            json={
                'name': 'acl',
                'version': '1.4',
                'somekey': 'value',
                '_links': {
                    'sw360:component': {
                        'href': SW360_BASE_URL + 'components/7b4'}}})
        r = Release().get(self.lib, "123")
        self.assertEqual(r.name, "acl")
        self.assertEqual(r.details["somekey"], "value")
        self.assertEqual(len(r.purls), 0)
        self.assertEqual(r.component_id, "7b4")


if __name__ == "__main__":
    unittest.main()
