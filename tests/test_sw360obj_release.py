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
from packageurl import PackageURL


class Sw360ObjTestRelease(Sw360ObjTestBase):
    def test_repr(self):
        r = Release(id_="123", name="TestCmp", version="1.4",
                    downloadurl="http://www")

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
        r = Release.get(self.lib, "123")
        self.assertEqual(r.name, "acl")
        self.assertEqual(r.details["somekey"], "value")
        self.assertEqual(len(r.purls), 0)
        self.assertEqual(r.parent.id, "7b4")

    @responses.activate
    def test_get_release_extid(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/123",
            json={
                'name': 'acl',
                'version': '1.4',
                'externalIds': {'some.id': '7105'}})
        r = Release.get(self.lib, "123")
        self.assertEqual(r.external_ids["some.id"], "7105")
        self.assertEqual(len(r.purls), 0)

    @responses.activate
    def test_get_release_purl_string(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/113",
            json={
                'name': 'acl',
                'version': '1.4',
                'externalIds': {
                  'package-url': 'pkg:deb/debian/linux@4.19.98-1?arch=source'}})
        r = Release.get(self.lib, "113")
        self.assertEqual(len(r.purls), 1)
        purl = next(iter(r.purls))
        self.assertEqual(purl.name, "linux")
        self.assertEqual(purl.version, "4.19.98-1")

        r = Release.get(self.lib, "113")
        self.assertEqual(len(r.purls), 1)

        responses.replace(
            responses.GET,
            SW360_BASE_URL + "releases/113",
            json={
                'name': 'acl',
                'version': '1.4'})
        r = Release.get(self.lib, "113")
        self.assertEqual(len(r.purls), 1)

    @responses.activate
    def test_get_release_purl_invalid(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/120",
            json={
                'name': 'acl',
                'version': '1.4',
                'externalIds': {
                  'package-url': 'pkg:huhu'}})
        r = Release.get(self.lib, "120")
        self.assertEqual(len(r.purls), 0)
        self.assertEqual(r.external_ids["package-url"], "pkg:huhu")

    @responses.activate
    def test_get_release_purl_array(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/123",
            json={
                'name': 'acl',
                'version': '1.4',
                'externalIds': {
                  'package-url': [
                    'pkg:deb/debian/linux@4.19.98-1?arch=source',
                    'pkg:deb/debian/linux-signed-amd64@4.19.98%2B1?arch=source']}})
        r = Release.get(self.lib, "123")
        self.assertEqual(len(r.purls), 2)
        self.assertIn(PackageURL.from_string("pkg:deb/debian/linux@4.19.98-1?arch=source"), r.purls)
        self.assertIn(PackageURL.from_string("pkg:deb/debian/linux-signed-amd64@4.19.98+1?arch=source"), r.purls)

    @responses.activate
    def test_get_release_purl_strarray(self):
        # as of 2022-04, SW360 returns multiple external IDs as JSON string
        responses.add(
            responses.GET,
            SW360_BASE_URL + "releases/123",
            json={
                'name': 'acl',
                'version': '1.4',
                'externalIds': {
                  'package-url': '["pkg:deb/debian/linux@4.19.98-1?arch=source",'
                                 ' "pkg:deb/debian/linux-signed-amd64@4.19.98%2B1?arch=source"]'}})
        r = Release.get(self.lib, "123")
        self.assertEqual(len(r.purls), 2)
        self.assertIn(PackageURL.from_string("pkg:deb/debian/linux@4.19.98-1?arch=source"), r.purls)
        self.assertIn(PackageURL.from_string("pkg:deb/debian/linux-signed-amd64@4.19.98+1?arch=source"), r.purls)


if __name__ == "__main__":
    unittest.main()
