# -------------------------------------------------------------------------------
# (c) 2020 Siemens AG
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import os
import sys
import tempfile
import warnings
import unittest

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error   # noqa: E402


class Sw360TestAttachments(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

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

    def _my_matcher(self):
        """
        Helper method to display the JSON parameters of a REST call.
        """
        def display_json_params(request_body):
            print("MyMatcher:'" + request_body + "'")
            return True

        return display_json_params

    @responses.activate
    def test_get_attachment_infos_by_hash(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/attachments?sha1=5f392efeb0934339fb6b0f3e021076db19fad164",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "CLIXML_angular-10.0.7.xml", "sha1": "5f392efeb0934339fb6b0f3e021076db19fad164", "attachmentType": "COMPONENT_LICENSE_INFO_XML"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.get_attachment_infos_by_hash("5f392efeb0934339fb6b0f3e021076db19fad164")
        self.assertIsNotNone(data)
        self.assertTrue("_embedded" in data)
        self.assertTrue("sw360:attachments" in data["_embedded"])
        att_info = data["_embedded"]["sw360:attachments"]
        self.assertTrue(len(att_info) > 0)
        self.assertEqual("5f392efeb0934339fb6b0f3e021076db19fad164", att_info[0]["sha1"])

    @responses.activate
    def test_get_attachment_infos_for_release(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/1234/attachments",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "CLIXML.xml", "sha1": "ABCD", "attachmentType": "COMPONENT_LICENSE_INFO_XML", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/A123"}}}, {"filename": "angular.zip", "sha1": "EFGH", "attachmentType": "SOURCE", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/B123" } }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        attachments = lib.get_attachment_infos_for_release("1234")
        self.assertIsNotNone(attachments)
        self.assertTrue(len(attachments) > 0)
        self.assertEqual("ABCD", attachments[0]["sha1"])

    @responses.activate
    def test_get_attachment_infos_for_component(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/1234/attachments",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "angular.zip", "sha1": "EFGH", "attachmentType": "SOURCE", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/B123" } }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        attachments = lib.get_attachment_infos_for_component("1234")
        self.assertIsNotNone(attachments)
        self.assertTrue(len(attachments) > 0)

    @responses.activate
    def test_get_attachment_infos_for_project(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/projects/1234/attachments",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "angular.zip", "sha1": "EFGH", "attachmentType": "SOURCE", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/B123" } }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        attachments = lib.get_attachment_infos_for_project("1234")
        self.assertIsNotNone(attachments)
        self.assertTrue(len(attachments) > 0)

    @responses.activate
    def test_get_attachment_by_url(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/1234/attachments/5678",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "angular.zip", "sha1": "EFGH", "attachmentType": "SOURCE", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/B123" } }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        attachments = lib.get_attachment_by_url(self.MYURL + "resource/api/releases/1234/attachments/5678")  # noqa
        self.assertIsNotNone(attachments)
        self.assertTrue(len(attachments) > 0)

    @responses.activate
    def test_download_release_attachment_no_resource_id(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.download_release_attachment("myfile.txt", None, "5678")

        self.assertEqual("No resource id provided!", context.exception.message)

    @responses.activate
    def test_download_release_attachment_no_attachment_id(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        with self.assertRaises(SW360Error) as context:
            lib.download_release_attachment("myfile.txt", "1234", None)

        self.assertEqual("No attachment id provided!", context.exception.message)

    @responses.activate
    def test_download_release_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/releases/1234/attachments/5678",
            body='xxxx',
            status=200,
            content_type="application/text",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "test_attachment.txt")
        if os.path.exists(filename):
            os.remove(filename)

        self.assertFalse(os.path.exists(filename))
        lib.download_release_attachment(filename, "1234", "5678")
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)
        os.removedirs(tmpdir)

    @responses.activate
    def test_download_project_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/projects/1234/attachments/5678",
            body='xxxx',
            status=200,
            content_type="application/text",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "test_attachment.txt")
        if os.path.exists(filename):
            os.remove(filename)

        self.assertFalse(os.path.exists(filename))
        lib.download_project_attachment(filename, "1234", "5678")
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)
        os.removedirs(tmpdir)

    @responses.activate
    def test_download_component_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/components/1234/attachments/5678",
            body='xxxx',
            status=200,
            content_type="application/text",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "test_attachment.txt")
        if os.path.exists(filename):
            os.remove(filename)

        self.assertFalse(os.path.exists(filename))
        lib.download_component_attachment(filename, "1234", "5678")
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)
        os.removedirs(tmpdir)

    @responses.activate
    def test_get_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/attachments/1234",  # noqa
            body='{"_embedded": {"sw360:attachments": [{"filename": "angular.zip", "sha1": "EFGH", "attachmentType": "SOURCE", "_links": { "self": { "href": "https://sw360.siemens.com/resource/api/attachments/B123" } }}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        attachments = lib.get_attachment("1234")
        self.assertIsNotNone(attachments)
        self.assertTrue(len(attachments) > 0)

    @responses.activate
    def test_upload_resource_attachment_no_resource_type(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))
        with self.assertRaises(SW360Error) as context:
            lib._upload_resource_attachment(None, "123", filename)

        self.assertTrue(context.exception.message.startswith("Invalid resource type provided!"))
        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass

    @responses.activate
    def test_upload_attachment_file_does_not_exist(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        filename = "_does_not_exist_filename.dat"
        self.assertFalse(os.path.exists(filename))
        with self.assertRaises(SW360Error) as context:
            lib.upload_release_attachment("1234", filename)

        self.assertTrue(context.exception.message.startswith("ERROR: file not found:"))

    @responses.activate
    def test_upload_release_attachment_no_release_id(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))
        with self.assertRaises(SW360Error) as context:
            lib.upload_release_attachment(None, filename)

        self.assertTrue(context.exception.message.startswith("Invalid resource id provided!"))
        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass

    @responses.activate
    def test_upload_release_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.POST,
            url=self.MYURL + "resource/api/releases/1234/attachments",  # noqa
            body='xxx',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))
        lib.upload_release_attachment("1234", filename)
        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass

    @responses.activate
    def test_upload_release_attachment_failed(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.POST,
            url=self.MYURL + "resource/api/releases/1234/attachments",  # noqa
            body='{"timestamp": "2020-12-10T07:22:06.1685Z", "status": "500", "error": "Internal Server Error", "message": "forbidded"}',  # noqa
            status=500,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))

        with self.assertRaises(SW360Error) as context:
            lib.upload_release_attachment("1234", filename)

        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass

        self.assertEqual(500, context.exception.response.status_code)
        self.assertEqual("500", context.exception.details["status"])
        self.assertEqual("Internal Server Error", context.exception.details["error"])
        self.assertEqual("forbidded", context.exception.details["message"])

    @responses.activate
    def test_upload_component_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.POST,
            url=self.MYURL + "resource/api/components/223355/attachments",  # noqa
            body='xxx',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))
        lib.upload_component_attachment("223355", filename, upload_type="DOCUMENT")
        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass

    @responses.activate
    def test_upload_project_attachment(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        lib.force_no_session = True
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.POST,
            url=self.MYURL + "resource/api/projects/666/attachments",  # noqa
            body='xxx',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        _, filename = tempfile.mkstemp()
        self.assertTrue(os.path.exists(filename))
        lib.upload_project_attachment(
            "666", filename, upload_type="README_OSS", upload_comment="The new RDM!")
        try:
            os.remove(filename)
        except OSError:
            # ignore
            pass


if __name__ == "__main__":
    unittest.main()
