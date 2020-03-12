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
from sw360 import Component


class Sw360ObjTestComponent(Sw360ObjTestBase):
    def test_repr(self):
        comp = Component(component_id="123", name="TestCmp", homepage="http://www",
                         component_type="INTERNAL")
        comp = eval(repr(comp))
        assert comp.id == "123"
        assert comp.name == "TestCmp"
        self.assertEqual(str(comp), "TestCmp (123)")

        comp = Component()
        comp = eval(repr(comp))
        assert comp.id is None
        assert comp.name is None

    @responses.activate
    def test_get_component(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "components/123",
            json={
                'name': 'acl',
                'somekey': 'value',
                '_embedded': {
                    'sw360:releases': [{
                        'name': 'acl',
                        'version': '2.2',
                        '_links': {'self': {
                            'href': SW360_BASE_URL + 'releases/7c4'}}}]}})
        comp = Component().get(self.lib, "123")
        self.assertEqual(comp.name, "acl")
        self.assertEqual(comp.details["somekey"], "value")
        self.assertEqual(len(comp.releases), 1)
        self.assertEqual(comp.releases["7c4"].component_id, "123")


if __name__ == "__main__":
    unittest.main()
