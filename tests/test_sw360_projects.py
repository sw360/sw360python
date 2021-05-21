# -------------------------------------------------------------------------------
# (c) 2019-2021 Siemens AG
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import os
import sys
import tempfile
import unittest
import warnings

import responses

sys.path.insert(1, "..")

from sw360 import SW360, SW360Error   # noqa: E402


class Sw360TestProjects(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)

    def get_logged_in_lib(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        return lib

    @responses.activate
    def test_get_project(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        p = lib.get_project("123")
        self.assertEqual("My Testproject", p["name"])

        self.assertIsNotNone(lib.session)
        lib.close_api()
        self.assertIsNone(lib.session)

    @responses.activate
    def test_get_project_not_logged_in(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.get_project("123")

        self.assertTrue(context.exception.message.startswith("login_api needs to be called first"))

    @responses.activate
    def test_get_project_not_found(self):
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        # lib.force_no_session = True

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123456",
            body='{"timestamp":"2020-11-13T17:39:28.689358Z","status":404,"error":"Not Found","message":"Requested Project Not Found"}',  # noqa
            status=404,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        with self.assertRaises(SW360Error) as context:
            lib.get_project("123456")

        self.assertEqual(404, context.exception.response.status_code)
        self.assertEqual("Not Found", context.exception.details["error"])
        self.assertEqual("Requested Project Not Found", context.exception.details["message"])

    @responses.activate
    def test_get_project_releases(self):
        lib = self.get_logged_in_lib()
        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/releases?transitive=false",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_project_releases("123")
        self.assertIsNotNone(releases)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/releases?transitive=true",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        releases = lib.get_project_releases("123", True)
        self.assertIsNotNone(releases)

    @responses.activate
    def test_get_project_by_url(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123",
            body='{"name": "My Testproject"}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        p = lib.get_project_by_url(self.MYURL + "resource/api/projects/123")
        self.assertEqual("My Testproject", p["name"])

    @responses.activate
    def test_get_projects(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject"}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects()
        self.assertIsNotNone(projects)
        self.assertTrue("_embedded" in projects)
        self.assertTrue("sw360:projects" in projects["_embedded"])
        self.assertEqual("My Testproject", projects["_embedded"]["sw360:projects"][0]["name"])

    @responses.activate
    def test_get_projects_with_details(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?allDetails=true",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject"}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects(all_details=True)
        self.assertIsNotNone(projects)
        self.assertTrue("_embedded" in projects)
        self.assertTrue("sw360:projects" in projects["_embedded"])
        self.assertEqual("My Testproject", projects["_embedded"]["sw360:projects"][0]["name"])

    @responses.activate
    def test_get_projects_with_paging(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?page=1&page_entries=2&sort=name%2Cdesc",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject"}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects(page=1, page_size=2)
        self.assertIsNotNone(projects)
        self.assertTrue("_embedded" in projects)
        self.assertTrue("sw360:projects" in projects["_embedded"])
        self.assertEqual("My Testproject", projects["_embedded"]["sw360:projects"][0]["name"])

    @responses.activate
    def test_get_projects_with_paging_and_details(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?allDetails=true?page=3&page_entries=4&sort=name%2Cdesc",  # noqa
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject"}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects(all_details=True, page=3, page_size=4)
        self.assertIsNotNone(projects)
        self.assertTrue("_embedded" in projects)
        self.assertTrue("sw360:projects" in projects["_embedded"])
        self.assertEqual("My Testproject", projects["_embedded"]["sw360:projects"][0]["name"])

    @responses.activate
    def test_get_projects_by_type(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?type=SERVICE",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject", "projectType": "SERVICE"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_type("SERVICE")
        self.assertIsNotNone(projects)
        self.assertTrue(len(projects) > 0)
        self.assertEqual("My Testproject", projects[0]["name"])
        self.assertEqual("SERVICE", projects[0]["projectType"])

    @responses.activate
    def test_get_project_names(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject", "version" : "1.0.0"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        project_names = lib.get_project_names()
        self.assertIsNotNone(project_names)
        self.assertTrue(len(project_names) > 0)
        self.assertEqual("My Testproject, 1.0.0", project_names[0])

    @responses.activate
    def test_get_projects_by_name(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?name=My",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_name("My")
        self.assertIsNone(projects)

    @responses.activate
    def test_get_projects_by_name_no_result(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?name=My",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject"}]}}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_name("My")
        self.assertIsNotNone(projects)
        self.assertTrue(len(projects) > 0)
        self.assertEqual("My Testproject", projects[0]["name"])

    @responses.activate
    def test_get_projects_by_external_id(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/searchByExternalIds?myid=9999",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject", "externalIds": {"myid": "9999"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_external_id("myid", "9999")
        self.assertIsNotNone(projects)
        self.assertTrue(len(projects) > 0)
        self.assertEqual("My Testproject", projects[0]["name"])
        self.assertTrue(len(projects[0]["externalIds"]) > 0)
        self.assertEqual("9999", projects[0]["externalIds"]["myid"])

    @responses.activate
    def test_get_projects_by_external_id_no_result(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/searchByExternalIds?myid=9999",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_external_id("myid", "9999")
        self.assertIsNone(projects)

    @responses.activate
    def test_get_projects_by_group(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?group=SI",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject", "externalIds": {"com.siemens.code.project.id": "13171"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_group("SI")
        self.assertIsNotNone(projects)
        self.assertTrue(len(projects) > 0)
        self.assertEqual("My Testproject", projects[0]["name"])

    @responses.activate
    def test_get_projects_by_group_with_details(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?allDetails?group=SI",
            body='{"_embedded": {"sw360:projects": [{"name": "My Testproject", "externalIds": {"com.siemens.code.project.id": "13171"}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_group("SI", all_details=True)
        self.assertIsNotNone(projects)
        self.assertTrue(len(projects) > 0)
        self.assertEqual("My Testproject", projects[0]["name"])

    @responses.activate
    def test_get_projects_by_group_no_result(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects?group=SI",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        projects = lib.get_projects_by_group("SI")
        self.assertIsNone(projects)

    @responses.activate
    def test_download_license_info(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/licenseinfo?generatorClassName=XhtmlGenerator&variant=DISCLOSURE",  # noqa
            body='xxxx',
            status=200,
            content_type="application/text",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "rdm.html")
        if os.path.exists(filename):
            os.remove(filename)

        self.assertFalse(os.path.exists(filename))
        lib.download_license_info("123", filename, generator="XhtmlGenerator")
        self.assertTrue(os.path.exists(filename))
        os.remove(filename)
        os.removedirs(tmpdir)

    @responses.activate
    def test_get_project_vulnerabilities(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/vulnerabilities",
            body='{"_embedded": {"sw360:vulnerabilityDToes": [{"priority": "2 - major", "action": "Follow Recommendation"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.get_project_vulnerabilities("123")
        self.assertIsNotNone(data)
        self.assertTrue("_embedded" in data)
        self.assertTrue("sw360:vulnerabilityDToes" in data["_embedded"])
        vulnerabilities = data["_embedded"]["sw360:vulnerabilityDToes"]
        self.assertIsNotNone(vulnerabilities)
        self.assertTrue(len(vulnerabilities) > 0)
        self.assertEqual("2 - major", vulnerabilities[0]["priority"])

    @responses.activate
    def test_get_project_vulnerabilities_no_result(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/vulnerabilities",
            body='{}',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        data = lib.get_project_vulnerabilities("123")
        self.assertIsNone(data)

    @responses.activate
    def test_create_new_project(self):
        lib = self.get_logged_in_lib()
        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects",
            json={
                # server returns complete project, here we only mock a part of it
                'name': 'NewProduct',
                '_links': {
                    'self': {
                        'href': self.MYURL+'resource/api/projects/0206'
                    }
                }
            },
            match=[
              responses.json_params_matcher({
                "name": "NewProduct", "version": "42",
                "description": "Example Product",
                "projectType": "PRODUCT", "visibility": "EVERYONE",
              })
            ]
        )
        lib.create_new_project(
            name="NewProduct", version="42",
            description="Example Product",
            project_type="PRODUCT", visibility="EVERYONE",
        )

    @responses.activate
    def test_create_new_project_already_exists(self):
        lib = self.get_logged_in_lib()
        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects",
            json={
              "timestamp": "2020-12-13T20:32:17.799234Z", "status": 409,
              "error": "Conflict",
              "message": "sw360 project with name \'NewProduct\' already exists."
            },
            status=409,
            match=[
              responses.json_params_matcher({
                "name": "NewProduct", "version": "42",
                "description": "Example Product",
                "projectType": "PRODUCT", "visibility": "EVERYONE",
              })
            ]
        )
        with self.assertRaises(SW360Error) as context:
            lib.create_new_project(
                name="NewProduct", version="42",
                description="Example Product",
                project_type="PRODUCT", visibility="EVERYONE",
            )
        self.assertEqual(409, context.exception.response.status_code)

    @responses.activate
    def test_update_project(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            status=202,
        )

        project = {}
        project["name"] = "NewComponent"
        project["version"] = "9.99"
        project["projectType"] = "PRODUCT"

        lib.update_project(project, "123")

    @responses.activate
    def test_update_project_failed(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            status=404,
        )

        project = {}
        project["name"] = "NewComponent"
        project["version"] = "9.99"
        project["projectType"] = "PRODUCT"

        with self.assertRaises(SW360Error) as context:
            lib.update_project(project, "123")

        self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_update_project_releases_no_id(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            status=202,
        )

        with self.assertRaises(SW360Error) as context:
            lib.update_project_releases(None, None)

        self.assertEqual("No project id provided!", context.exception.message)

    @responses.activate
    def test_update_project_releases_fresh_prj(self):
        lib = self.get_logged_in_lib()
        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/releases?transitive=false",
            json={},
        )
        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects/123/releases",
            status=202,
        )
        lib.update_project_releases({}, "123", add=True)

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/124/releases?transitive=false",
            json={'_embedded': {'sw360:projects': []}},
        )
        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects/124/releases",
            status=202,
        )
        lib.update_project_releases({}, "124", add=True)

    @responses.activate
    def test_update_project_releases(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/releases?transitive=false",
            body='{"_embedded": {"sw360:releases": [{"name": "ngx-device-detector ", "version": "1.3.20","_links": {"self": {"href": "https://sw360.siemens.com/resource/api/releases/3a4865e453873ee00d924469ff40f391" }}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects/123/releases",
            body="4",
            status=202,
        )

        releases = {}
        lib.update_project_releases(releases, "123", add=True)

    @responses.activate
    def test_update_project_releases_failed(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/123/releases?transitive=false",
            body='{"_embedded": {"sw360:releases": [{"name": "ngx-device-detector ", "version": "1.3.20","_links": {"self": {"href": "https://sw360.siemens.com/resource/api/releases/3a4865e453873ee00d924469ff40f391" }}}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        responses.add(
            responses.POST,
            url=self.MYURL + "resource/api/projects/123/releases",
            body="4",
            status=404,
        )

        releases = {}
        with self.assertRaises(SW360Error) as context:
            lib.update_project_releases(releases, "123", add=True)

        self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_update_project_external_id_add_fresh_id(self):
        lib = self.get_logged_in_lib()

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/projects/123",  # noqa
            body='{"name": "Tethys.Logging", "version": "1.4.0", "externalIds": {"already-existing": "must-be-kept"}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        # add fresh id
        responses.add(
            responses.PATCH,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            match=[
              responses.json_params_matcher({"externalIds": {"already-existing": "must-be-kept", "package-url": "pkg:deb/debian/debootstrap?type=source"}})  # noqa
            ]
        )

        lib.update_project_external_id(
            "package-url",
            "pkg:deb/debian/debootstrap?type=source",
            "123")

    @responses.activate
    def test_delete_project(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            status=200,
        )

        lib.delete_project("123")

    @responses.activate
    def test_delete_project_no_id(self):
        lib = self.get_logged_in_lib()

        with self.assertRaises(SW360Error) as context:
            lib.delete_project(None)

        self.assertEqual("No project id provided!", context.exception.message)

    @responses.activate
    def test_delete_project_failed(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.DELETE,
            url=self.MYURL + "resource/api/projects/123",
            body="4",
            status=404,
        )

        with self.assertRaises(SW360Error) as context:
            lib.delete_project("123")

        self.assertEqual(404, context.exception.response.status_code)

    @responses.activate
    def test_get_users_of_project(self):
        lib = self.get_logged_in_lib()

        responses.add(
            responses.GET,
            url=self.MYURL + "resource/api/projects/usedBy/123",  # noqa
            body='{"_embedded": {"sw360:projects": [{"name": "xxx", "version": "4.5"}]}}',  # noqa
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN}
        )

        lib.get_users_of_project("123")


if __name__ == "__main__":
    unittest.main()
