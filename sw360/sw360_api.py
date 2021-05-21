# -------------------------------------------------------------------------------
# (c) 2019-2021 Siemens AG
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

"""Python interface to the Siemens SW360 platform"""

import json
import os
import requests


class SW360Error(IOError):
    """Base exception for SW360 operations

    :param message: a general error message
    :param response: the response object returned by the requests call
    :param url: the URL where the error occurred
    :type message: string
    :type response: object
    :type url: string
    """

    def __init__(self, response=None, url=None, message=None):
        self.message = message
        self.response = response
        self.url = url
        try:
            if response is not None:
                self.details = json.loads(response.text)
        except json.JSONDecodeError:
            self.details = None

        if message:
            super().__init__(message)
        else:
            super().__init__(str(response))


class SW360:
    """Python interface to the Siemens SW360 platform

    Authentication against a running SW360 instance is performed using an API token.
    The token will be sent as HTTP header using the format
    `Authorization: <token_type> <token>`. Check your SW360 REST API
    documentation for details on needed type and how to get the token.
    token_type is "Bearer" for an OAuth workflow and "Token" for tokens
    generated via the SW360 UI.

    :param url: URL of the SW360 instance
    :param token: The SW360 REST API token (the cryptic string without
     "Authorization:" and `token_type`).
    :param oauth2: flag inidacting whether this is an OAuth2 token
    :type url: string
    :type token: string
    :type oauth2: boolean
    """

    def __init__(self, url, token, oauth2=False):
        """Constructor"""
        if url[-1] != "/":
            url += "/"
        self.url = url
        self.session = None

        if oauth2:
            self.api_headers = {"Authorization": "Bearer " + token}
        else:
            self.api_headers = {"Authorization": "Token " + token}

        self.force_no_session = False

    def login_api(self, token=None):
        """Login to SW360 REST API. This used to have a `token` parameter
        due to historic reasons which is ignored.

        You need to call this before any other method accessing SW360.

        :raises SW360Error: if the login fails
        """
        if not self.force_no_session:
            self.session = requests.Session()
            self.session.headers = self.api_headers.copy()

        url = self.url + "resource/api/"
        try:
            if self.force_no_session:
                resp = requests.get(url, headers=self.api_headers)
            else:
                resp = self.session.get(url)

        except Exception as ex:
            raise SW360Error(None, url, message="Unable to login: " + repr(ex))

        if resp.ok:
            return True
        else:
            raise SW360Error(resp, url, message="Unable to login")

    def close_api(self):
        """A keep-alive HTTP session is used to access the SW360 REST API.
        This method allows to explicitely close the connection at a defined
        time. Normally, you don't need to call it - session is cleaned up
        automatically when needed."""
        if self.session is not None:
            self.session.close()
            self.session = None

    def api_get(self, url=None):
        """Request `url` from REST API and return json answer.

        :param url: the url to be requested
        :type url: string
        :return: JSON data
        :rtype: JSON
        :raises SW360Error: if there is a negative HTTP response
        """

        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.get(url, headers=self.api_headers)
        else:
            response = self.session.get(url)

        if response.ok:
            if response.status_code == 204:  # 204 = no content
                return None
            return response.json()

        raise SW360Error(response, url)

    def api_get_raw(self, url=None):
        """Request `url` from REST API and return raw result.

        :param url: the url to be requested
        :type url: string
        :return: the HTTP response
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.get(url, headers=self.api_headers)
        else:
            response = self.session.get(url)

        if response.ok:
            return response.text

        raise SW360Error(response, url)

    def _update_external_ids(self, current_data, ext_id_name, ext_id_value,
                             update_mode):
        """Internal helper function to prepare an update/addition of external
        id while preserving the others."""
        old_value = None
        if "externalIds" not in current_data:
            ext_id_data = {"externalIds": {ext_id_name: ext_id_value}}
        else:
            if ext_id_name in current_data["externalIds"]:
                old_value = current_data["externalIds"][ext_id_name]
            ext_id_data = {"externalIds": current_data["externalIds"]}
            ext_id_data["externalIds"][ext_id_name] = ext_id_value

        if update_mode == "delete":
            del ext_id_data["externalIds"][ext_id_name]

        if (update_mode == "overwrite"
                or (update_mode == "none" and old_value is None)
                or (update_mode == "delete" and old_value is not None)):
            update = True
        else:
            update = False

        return (old_value, ext_id_data, update)

    # ----- Projects ---------------------------------------------------------

    def get_project(self, project_id):
        """Get information of about a project

        API endpoint: GET /projects

        :param project_id: the id of the project to be requested
        :type project_id: string
        :return: a project
        :rtype: JSON project object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects/" + project_id)
        return resp

    def get_project_releases(self, project_id, transitive=False):
        """Get the releases of a project

        API endpoint: GET /projects/{id}/releases

        :param project_id: the id of the project to be requested
        :param transitive: flag whether also all transitive releases should get returned
        :type project_id: string
        :type transitive: boolean
        :return: JSON data
        :rtype: JSON
        :raises SW360Error: if there is a negative HTTP response
        """
        trans = "false"
        if transitive:
            trans = "true"
        resp = self.api_get(self.url + "resource/api/projects/"
                            + project_id + "/releases?transitive=" + trans)
        return resp

    def get_project_by_url(self, url):
        """Get information of about a project

        API endpoint: GET /projects

        :param url: the full url of the project to be requested
        :type url: string
        :return: a project
        :rtype: JSON project object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(url)
        return resp

    def get_projects(self, all_details=False, page=-1, page_size=-1):
        """Get all projects

        API endpoint: GET /projects

        :param all_details: retrieve all project details (optional))
        :type all_details: bool
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """

        full_url = self.url + "resource/api/projects"
        if all_details:
            full_url = full_url + "?allDetails=true"

        if page > -1:
            full_url = full_url + "?page=" + str(page) + "&page_entries="
            full_url = full_url + str(page_size) + "&sort=name%2Cdesc"

        resp = self.api_get(full_url)
        return resp

    def get_projects_by_type(self, project_type):
        """Get information of about all projects of a certain type

        API endpoint: GET /projects

        :param project_type: the full url of the project to be requested
        :type project_type: string, one of CUSTOMER, INTERNAL, PRODUCT, SERVICE, INNER_SOURCE
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects?type=" + project_type)
        resp = resp["_embedded"]["sw360:projects"]
        return resp

    def get_project_names(self):
        """Get all project names

        API endpoint: GET /projects

        :return: JSON data
        :rtype: JSON
        :raises SW360Error: if there is a negative HTTP response
        """
        projects = self.get_projects()
        projects = projects["_embedded"]["sw360:projects"]
        resp = []
        for key in projects:
            resp.append(key["name"] + ", " + key["version"])

        return resp

    def get_projects_by_name(self, name):
        """Get a project by its name

        API endpoint: GET /projects

        :param name: the project name or a prefix of it
        :type name: string
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects?name=" + name)
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:projects"]
        return resp

    def get_projects_by_external_id(self, ext_id_name, ext_id_value=""):
        """Get projects by external id. `ext_id_value` can be left blank to
        search for all projects with `ext_id_name`.

        API endpoint: GET /projects

        :param ext_id_name: the name of the external id to look for
        :param ext_id_value: the value of the external id to look for
        :type ext_id_name: string
        :type ext_id_value: string
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects/searchByExternalIds?"
                            + ext_id_name + "=" + ext_id_value)
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:projects"]
        return resp

    def get_projects_by_group(self, group, all_details=False):
        """Get projects by group.

        API endpoint: GET /projects

        :param group: the group the projects shall belong to
        :type group: string
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/projects?group=" + group
        if all_details:
            full_url = self.url + "resource/api/projects?allDetails?group=" + group

        resp = self.api_get(full_url)
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:projects"]
        return resp

    def download_license_info(self, project_id, filename, generator="XhtmlGenerator",
                              variant="DISCLOSURE"):
        """Gets the license information, aka Readme_OSS for the project
        with the given id

        API endpoint: GET /projects

        :param project_id: the id of the project to be deleted
        :param filename: the filename to be used
        :type project_id: string
        :type filename: string
        """
        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        url = self.url + "resource/api/projects/" + project_id + \
            "/licenseinfo?generatorClassName=" + generator + "&variant=" + variant
        req = requests.get(url, allow_redirects=True, headers=hdr)
        open(filename, "wb").write(req.content)

    def get_project_vulnerabilities(self, project_id):
        """Get the security vulnerabilities for the specified project.

        API endpoint: GET /projects/id/vulnerabilities

        :param project_id: the id of the project
        :type project_id: string
        :return: list of security vulnerabilities
        :rtype: JSON object
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/projects/" + project_id + "/vulnerabilities"
        resp = self.api_get(full_url)
        if not resp:
            return None

        return resp

    def create_new_project(self, name, project_type, visibility,
                           description="", version="", project_details={}):
        """Create a new project.

        The parameters list only the most common project attributes, check the
        SW360 REST API documentation and use `project_details` to add more if
        needed.

        API endpoint: POST /projects

        :param name: name of the new project
        :param project_type: one of "CUSTOMER", "INTERNAL", "PRODUCT", "SERVICE", "INNER_SOURCE"
        :param visibility: one of "PRIVATE", "ME_AND_MODERATORS",
          "BUISNESSUNIT_AND_MODERATORS" (no typo), "EVERYONE"
        :param description: description for new project
        :param version: version of project/product etc., if applicable
        :param project_details: further project details as defined by SW360 REST API
        :type name: string
        :type project_type: string
        :type visibility: string
        :type description: string
        :type version: string
        :type project_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """
        for param in "name", "visibility", "version", "description":
            project_details[param] = locals()[param]
        project_details["projectType"] = project_type

        url = self.url + "resource/api/projects"
        response = requests.post(
            url, json=project_details, headers=self.api_headers
        )

        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_project(self, project, project_id):
        """Update an existing project

        API endpoint: PATCH /projects

        :param project: the new project data
        :param project_id: the id of the project to be deleted
        :type project: JSON
        :type project_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """
        # 2019-04-03: error 405 - method not allowed
        url = self.url + "resource/api/projects/" + project_id
        response = requests.patch(url, json=project, headers=self.api_headers)

        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_project_releases(self, releases, project_id, add=False):
        """Update the releases of an existing project. If `add` is True,
        given `releases` are added to the project, otherwise, the existing
        releases will be replaced.

        API endpoint: POST /projects/<id>/releases

        :param releases: list of relase_ids to be linked in the project
        :param project_id: the id of the project to modify
        :param add: add given releases if set to True, replace otherwise
        :type releases: list of release_id strings
        :type project_id: string
        :type add: boolean
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not project_id:
            raise SW360Error(message="No project id provided!")

        if add:
            old_releases = self.get_project_releases(project_id)
            if (old_releases is not None and "_embedded" in old_releases
                    and "sw360:releases" in old_releases["_embedded"]):
                old_releases = old_releases["_embedded"]["sw360:releases"]
                old_releases = [r["_links"]["self"]["href"] for r in old_releases]
                old_releases = [r.split("/")[-1] for r in old_releases]
                releases = old_releases + list(releases)

        url = self.url + "resource/api/projects/" + project_id + "/releases"
        response = requests.post(url, json=releases, headers=self.api_headers)

        if response.ok:
            return True

        raise SW360Error(response, url)

    def update_project_external_id(self, ext_id_name, ext_id_value,
                                   project_id, update_mode="none"):
        """Set or update external id of a project. If the id is already set, it
        will only be changed if `update_mode=="overwrite"`. The id can be
        deleted using `update_mode=="delete"`.

        The method will return the old value of the external id or None if it
        was not set.

        API endpoint: PATCH /projects

        :param ext_id_name: name of the external id
        :param ext_id_value: value of the external id
        :param project_id: the id of the project to be updated
        :param update_mode: can be "none" (default), "overwrite" or "delete"
        :type ext_id_name: string
        :type ext_id_value: string
        :type project_id: string
        :type update_mode: string
        :return: old value of external id
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        complete_data = self.get_project(project_id)
        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_project(data, project_id)
        return old_value

    def delete_project(self, project_id):
        """Delete an existing project

        API endpoint: DELETE /projects

        :param project_id: the id of the project to be requested
        :type project_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """
        # 2019-04-03: error 405 - method not allowed

        if not project_id:
            raise SW360Error(message="No project id provided!")

        url = self.url + "resource/api/projects/" + project_id
        response = requests.delete(
            url, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def get_users_of_project(self, project_id):
        """Get information of about users of a project

        API endpoint: GET /projects/usedBy/{id}

        :param project_id: the id of the project to be requested
        :type project_id: string
        :return: all users of this project
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects/usedBy/" + project_id)
        return resp

    # ----- Releases ---------------------------------------------------------

    def get_release(self, release_id):
        """Get information of about a release

        API endpoint: GET /releases/{id}

        :param release_id: the id of the release to be requested
        :type release_id: string
        :return: a release
        :rtype: JSON release object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/releases/" + release_id)
        return resp

    def get_release_by_url(self, release_url):
        """Get information of about a release

        API endpoint: GET /releases

        :param url: the full url of the release to be requested
        :type url: string
        :return: a release
        :rtype: JSON release object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(release_url)
        return resp

    def get_all_releases(self, fields=None, all_details=False):
        """Get information of about all releases

        API endpoint: GET /releases

        :param all_details: retrieve all project details (optional))
        :type all_details: bool
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/releases"
        if all_details:
            full_url = full_url + "?allDetails=true"

        if fields:
            full_url = full_url + "?fields=" + fields

        resp = self.api_get(full_url)

        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:releases"]
        return resp

    def get_releases_by_external_id(self, ext_id_name, ext_id_value=""):
        """Get releases by external id. `ext_id_value` can be left blank to
        search for all releases with `ext_id_name`.

        API endpoint: GET /releases

        :param ext_id_name: the name of the external id to look for
        :param ext_id_value: the value of the external id to look for
        :type ext_id_name: string
        :type ext_id_value: string
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(
            self.url
            + "resource/api/releases/searchByExternalIds?"
            + ext_id_name + "=" + ext_id_value
        )
        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:releases"]
        return resp

    def create_new_release(self, name, version, component_id, release_details={}):
        """Create a new release

        API endpoint: POST /releases

        :param name: name of new release (usually set to component name)
        :param version: version string of new release (e.g. "1.0")
        :param component_id: SW360 ID of component in which release shall be created
        :param release_details: further release details as defined by SW360 REST API
        :type name: string
        :type version: string
        :type component_id: string
        :type release_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        for param in "name", "version":
            release_details[param] = locals()[param]
        release_details["componentId"] = component_id

        url = self.url + "resource/api/releases"
        response = requests.post(
            url, json=release_details, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_release(self, release, release_id):
        """Update an existing release

        API endpoint: PATCH /releases

        :param release: the new release data
        :param release_id: the id of the release to be deleted
        :type release: JSON
        :type release_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id
        response = requests.patch(url, json=release, headers=self.api_headers)
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_release_external_id(self, ext_id_name, ext_id_value,
                                   release_id, update_mode="none"):
        """Set or update external id of a release. If the id is already set, it
        will only be changed if `update_mode=="overwrite"`. The id can be
        deleted using `update_mode=="delete"`.

        The method will return the old value of the external id or None if it
        was not set.

        API endpoint: PATCH /releases

        :param ext_id_name: name of the external id
        :param ext_id_value: value of the external id
        :param release_id: the id of the release to be updated
        :param update_mode: can be "none" (default), "overwrite" or "delete"
        :type ext_id_name: string
        :type ext_id_value: string
        :type release_id: string
        :type update_mode: string
        :return: old value of external id
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        complete_data = self.get_release(release_id)
        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_release(data, release_id)
        return old_value

    def delete_release(self, release_id):
        """Delete an existing release

        API endpoint: DELETE /releases

        :param release_id: the id of the release to be deleted
        :type release_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id
        response = requests.delete(
            url, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def get_users_of_release(self, release_id):
        """Get information of about the users of a release

        API endpoint: GET /releases/usedBy/{id}

        :param release_id: the id of the release to be requested
        :type release_id: string
        :return: all users of this release
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/releases/usedBy/" + release_id)
        return resp

    # ----- Components -------------------------------------------------------

    def get_all_components(self, fields=None, page=-1, page_size=-1):
        """Get information of about all components

        API endpoint: GET /components

        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        if fields:
            url = self.url + "resource/api/components?fields=" + fields
        else:
            url = self.url + "resource/api/components"

        if page > -1:
            url = url + "?page=" + str(page) + "&page_entries="
            url = url + str(page_size) + "&sort=name%2Cdesc"

        resp = self.api_get(url)
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:components"]
        return resp

    def get_components_by_type(self, component_type):
        """Get information of about all components for certain type

        API endpoint: GET /components

        :param component_type: the type of the component to be requested, one
         of INTERNAL, OSS, COTS, FREESOFTWARE, INNER_SOURCE, SERVICE
        :type component_type: string
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components?type=" + component_type)
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:components"]
        return resp

    def get_component(self, component_id):
        """Get information of about a component

        API endpoint: GET /components/{id}

        :param component_id: the id of the component to be requested
        :type component_id: string
        :return: a component
        :rtype: JSON component object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components/" + component_id)
        return resp

    def get_component_by_url(self, component_url):
        """Get information of about a component

        API endpoint: GET /components

        :param url: the full url of the component to be requested
        :type url: string
        :return: a component
        :rtype: JSON component object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(component_url)
        return resp

    def get_component_by_name(self, component_name):
        """Get information of about a component

        API endpoint: GET /components

        :param component_name: the name of the component to look for
        :type component_name: string
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components?name=" + component_name)
        return resp

    def get_components_by_external_id(self, ext_id_name, ext_id_value=""):
        """Get components by external id. `ext_id_value` can be left blank to
        search for all components with `ext_id_name`.

        API endpoint: GET /components

        :param ext_id_name: the name of the external id to look for
        :param ext_id_value: the value of the external id to look for
        :type ext_id_name: string
        :type ext_id_value: string
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(
            self.url
            + "resource/api/components/searchByExternalIds?"
            + ext_id_name
            + "="
            + ext_id_value
        )
        if resp and ("_embedded" in resp) and ("sw360:components" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:components"]
        return resp

    def create_new_component(self, name, description, component_type, homepage,
                             component_details={}):
        """Create a new component

        API endpoint: POST /components

        :param name: name of the new component
        :param description: description of the new component
        :param component_type: type of the new component, one of
         "INTERNAL", "OSS", "COTS", "FREESOFTWARE", "INNER_SOURCE", "SERVICE", "CODE_SNIPPET"
        :param homepage: homepage url of the new component
        :param component_details: further component details as defined by SW360 REST API
        :type name: string
        :type description: string
        :type component_type: string
        :type homepage: string
        :type component_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/components"

        for param in "name", "description", "homepage":
            component_details[param] = locals()[param]
        component_details["componentType"] = component_type

        response = requests.post(
            url, json=component_details, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_component(self, component, component_id):
        """Update an existing component

        API endpoint: PATCH /components

        :param component: the new vedor data
        :param component_id: the id of the component to be updated
        :type component: JSON vendor object
        :type component_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not component_id:
            raise SW360Error(message="No component id provided!")

        url = self.url + "resource/api/components/" + component_id
        response = requests.patch(
            url, json=component, headers=self.api_headers,
        )

        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_component_external_id(self, ext_id_name, ext_id_value,
                                     component_id, update_mode="none"):
        """Set or update external id of a component. If the id is already set, it
        will only be changed if `update_mode=="overwrite"`. The id can be
        deleted using `update_mode=="delete"`.

        The method will return the old value of the external id or None if it
        was not set.

        API endpoint: PATCH /components

        :param ext_id_name: name of the external id
        :param ext_id_value: value of the external id
        :param component_id: the id of the component to be updated
        :param update_mode: can be "none" (default), "overwrite" or "delete"
        :type ext_id_name: string
        :type ext_id_value: string
        :type component_id: string
        :type update_mode: string
        :return: old value of external id
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        complete_data = self.get_component(component_id)
        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_component(data, component_id)
        return old_value

    def delete_component(self, component_id):
        """Delete an existing component

        API endpoint: DELETE /components

        :param component_id: the id of the component to be deleted
        :type component_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not component_id:
            raise SW360Error(message="No component id provided!")

        url = self.url + "resource/api/components/" + component_id
        response = requests.delete(
            url, headers=self.api_headers,
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def get_users_of_component(self, component_id):
        """Get information of about the users of a component

        API endpoint: GET /components/usedBy/{id}

        :param component_id: the id of the component to be requested
        :type component_id: string
        :return: all users of this component
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components/usedBy/" + component_id)
        return resp

    # ----- Vendor ----------------------------------------------------------

    def get_vendor(self, vendor_id):
        """Returns a vendor

        API endpoint: GET /vendors/{id}

        :param vendor_id: the id of the vendor to be requested
        :type vendor_id: string
        :return: a vendor
        :rtype: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vendors/" + vendor_id)
        return resp

    def create_new_vendor(self, vendor):
        """Create a new vendor

        API endpoint: POST /vendors

        :param vendor: the new vedor data
        :type vendor: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/vendors"
        response = requests.post(
            url, json=vendor, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_vendor(self, vendor, vendor_id):
        """Update an existing vendor

        API endpoint: PATCH /vendors

        :param vendor_id: the id of the vendor to be updated
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        # 2019-04-03: error 405 - not allowed

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id
        response = requests.patch(
            url, json=vendor, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def delete_vendor(self, vendor_id):
        """Delete an existing vendor

        API endpoint: DELETE /vendors

        :param vendor_id: the id of the vendor
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        # 2019-04-03: error 405 - not allowed

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id
        response = requests.delete(
            url, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    # ----- Attachments ------------------------------------------------------
    def get_attachment_infos_by_hash(self, hashvalue):
        """Get information about attachments with a given sha1 hash value.

        This usually returns zero or one result, but if the same binary file
        was uploaded and attached to multiple sw360 resources, it will return
        all matching attachments for the given hash.

        API endpoint: GET /attachments?sha1=
        """

        resp = self.api_get(
            self.url
            + "resource/api/attachments?sha1=" + hashvalue
        )
        return resp

    def get_attachment_infos_for_resource(self, resource_type, resource_id):
        """Get information about the attachments of a specific resource.

        Usually, you don't need to call this directly, but use one of the
        specific get_attachment_infos_for_{release,component,project} functions.
        """

        resp = self.api_get(
            self.url
            + "resource/api/"
            + resource_type
            + "/"
            + resource_id
            + "/attachments"
        )
        resp = resp["_embedded"]["sw360:attachments"]
        return resp

    def get_attachment_infos_for_release(self, release_id):
        """Get information about the attachments of a release

        :param release_id: id of the release from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("releases", release_id)
        return resp

    def get_attachment_infos_for_component(self, component_id):
        """Get information about the attachments of a component

        :param component_id: id of the component from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("components", component_id)
        return resp

    def get_attachment_infos_for_project(self, project_id):
        """Get information about the attachments of a project

        :param project_id: id of the project from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("projects", project_id)
        return resp

    def get_attachment_by_url(self, url):
        """Get information about attachment.

        :param url: the full url of the attachment to be requested
        """
        resp = self.api_get(url)
        return resp

    def get_attachment(self, attachment_id):
        """Get information about an attachment

        API endpoint: GET /attachments

        :param attachment_id: id of the attachment
        """

        resp = self.api_get(self.url + "resource/api/attachments/" + attachment_id)
        return resp

    def download_release_attachment(self, filename, release_id, attachment_id):
        """Downloads an attachment of a release

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "releases", release_id, attachment_id
        )

    def download_project_attachment(self, filename, project_id, attachment_id):
        """Downloads an attachment of a project

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "projects", project_id, attachment_id
        )

    def download_component_attachment(self, filename, component_id, attachment_id):
        """Downloads an attachment of a component

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "components", component_id, attachment_id
        )

    def download_resource_attachment(self, filename, resource_type, resource_id, attachment_id):
        """Downloads an attachment from SW360 (only for internal use)

        API endpoint: GET /attachments
        """

        if not resource_id:
            raise SW360Error(message="No resource id provided!")

        if not attachment_id:
            raise SW360Error(message="No attachment id provided!")

        url = (
            self.url
            + "resource/api/"
            + resource_type
            + "/"
            + resource_id
            + "/attachments/"
            + attachment_id
        )
        self.download_attachment(filename, url)

    def download_attachment(self, filename, download_url):
        """Downloads an attachment from SW360

        API endpoint: GET /attachments
        """

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        req = requests.get(download_url, allow_redirects=True, headers=hdr)
        open(filename, "wb").write(req.content)

    def _upload_resource_attachment(self, resource_type, resource_id, upload_file,
                                    upload_type="SOURCE", upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for the resource with the given id
        using `upload_comment` for it. `upload_type` can be
        "DOCUMENT"
        "SOURCE"
        "CLEARING_REPORT"
        "COMPONENT_LICENSE_INFO_XML"
        "SOURCE_SELF"
        "BINARY"
        "BINARY_SELF"
        "LICENSE_AGREEMENT"
        "README_OSS"

        API endpoint: POST /attachments
        """
        if not os.path.exists(upload_file):
            raise SW360Error(message="ERROR: file not found: " + upload_file)

        if resource_type not in ("releases", "components", "projects"):
            raise SW360Error(message="Invalid resource type provided!")

        if type(resource_id) is not str:
            raise SW360Error(message="Invalid resource id provided!")

        filename = os.path.basename(upload_file)
        url = self.url + "resource/api/" + resource_type + "/" + resource_id + "/attachments"
        attachment_data = {"filename": filename,
                           "attachmentContentId": "2",
                           "createdComment": upload_comment,
                           "attachmentType": upload_type}
        file_data = {
            "file": (filename, open(upload_file, "rb"), "multipart/form-data"),
            "attachment": (
                "",  # dummy filename
                json.dumps(attachment_data),
                "application/json",
            ),
        }
        response = requests.post(url, headers=self.api_headers, files=file_data)
        if not response.ok:
            raise SW360Error(response, url)

    def upload_release_attachment(self, release_id, upload_file, upload_type="SOURCE",
                                  upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `release_id`,
        using `upload_comment` for it. `upload_type` can be
        "DOCUMENT"
        "SOURCE"
        "CLEARING_REPORT"
        "COMPONENT_LICENSE_INFO_XML"
        "SOURCE_SELF"
        "BINARY"
        "BINARY_SELF"
        "LICENSE_AGREEMENT"
        "README_OSS"

        API endpoint: POST /attachments
        """

        self._upload_resource_attachment(
            "releases", release_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)

    def upload_component_attachment(self, component_id, upload_file, upload_type="SOURCE",
                                    upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `component_id`,
        using `upload_comment` for it. `upload_type` can be
        "DOCUMENT"
        "SOURCE"
        "CLEARING_REPORT"
        "COMPONENT_LICENSE_INFO_XML"
        "SOURCE_SELF"
        "BINARY"
        "BINARY_SELF"
        "LICENSE_AGREEMENT"
        "README_OSS"

        API endpoint: POST /attachments
        """

        self._upload_resource_attachment(
            "components", component_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)

    def upload_project_attachment(self, project_id, upload_file, upload_type="SOURCE",
                                  upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `project_id` of,
        using `upload_comment` for it. `upload_type` can be
        "DOCUMENT"
        "SOURCE"
        "CLEARING_REPORT"
        "COMPONENT_LICENSE_INFO_XML"
        "SOURCE_SELF"
        "BINARY"
        "BINARY_SELF"
        "LICENSE_AGREEMENT"
        "README_OSS"

        API endpoint: POST /attachments
        """

        self._upload_resource_attachment(
            "projects", project_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)

    # ----- Licenses -------------------------------------------------------

    def get_all_licenses(self):
        """Get information of about all licenses

        API endpoint: GET /licenses

        :return: list of licenses
        :rtype: list of JSON license objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/licenses")
        if not resp:
            return None

        resp = resp["_embedded"]["sw360:licenses"]
        return resp

    def get_license(self, license_id):
        """Get information of about a license

        API endpoint: GET /licenses/{id}

        :param license_id: the id of the license to be requested
        :type license_id: string
        :return: a license
        :rtype: JSON license object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/licenses/" + license_id)
        return resp

    # ----- Vulnerabilities -------------------------------------------------------

    def get_all_vulnerabilities(self):
        """Get information of about all vulnerabilities

        API endpoint: GET /vulnerabilities

        :return: list of vulnerabilities
        :rtype: list of JSON vulnerability objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vulnerabilities")
        return resp

    def get_vulnerability(self, vulnerability_id):
        """Get information of about a vulnerability

        API endpoint: GET /vulnerabilities/{id}

        :param vulnerability_id: the id of the vulnerability to be requested
        :type vulnerability_id: string
        :return: a vulnerability
        :rtype: JSON vulnerability object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vulnerabilities/" + vulnerability_id)
        return resp

    # ----- Health -------------------------------------------------------

    def get_health_status(self):
        """Get information about the service's health.

        API endpoint: GET /health

        :return: service health status
        :rtype: JSON health status object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/health/")
        return resp

    # ----- Support ----------------------------------------------------------

    @classmethod
    def get_id_from_href(cls, href):
        """"Extracts the identifier from the href and returns it

        :param href: HAL href for a specific resource
        :type href: string (valid URL)
        :return: the id part of the href
        :rtype: string
        """

        pos = href.rfind("/")
        identifier = href[(pos + 1):]
        return identifier
