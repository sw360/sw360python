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
from sw360 import Project


class Sw360ObjTestProject(Sw360ObjTestBase):
    def test_repr(self):
        prj = Project(project_id="123", name="TestPrj", version="12")
        prj = eval(repr(prj))
        assert prj.id == "123"
        assert prj.name == "TestPrj"
        assert prj.version == "12"
        self.assertEqual(str(prj), "TestPrj 12 (123)")

        prj = Project()
        prj = eval(repr(prj))
        assert prj.id is None
        assert prj.name is None

    @responses.activate
    def test_get_project(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "projects/123",
            json={
                'name': 'MyProj',
                'version': '11.0',
                '_embedded': {
                    'sw360:releases': [{
                        'name': 'acl',
                        'version': '2.2',
                        '_links': {'self': {
                            'href': SW360_BASE_URL + 'releases/7c4'}}}]}})
        proj = Project().get(self.lib, "123")
        self.assertEqual(proj.name, "MyProj")
        self.assertEqual(proj.version, "11.0")
        self.assertEqual(len(proj.releases), 1)
        self.assertIsNone(proj.releases["7c4"].component_id)

        self.assertEqual(str(proj), "MyProj 11.0 (123)")


if __name__ == "__main__":
    unittest.main()
