# -------------------------------------------------------------------------------
# Copyright (c) 2019-2024 Siemens
# Copyright (c) 2022 BMW CarIT GmbH
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
# Authors: helio.chissini-de-castro@bmw.de
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional

import requests

from .base import BaseMixin
from .sw360error import SW360Error


class ProjectMixin(BaseMixin):
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def get_project_releases(self, project_id: str, transitive: bool = False) -> Any:
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

    def get_project_by_url(self, url: str) -> Optional[Dict[str, Any]]:
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

    def get_projects(self, all_details: bool = False, page: int = -1,
                     page_size: int = -1, sort: str = "") -> Optional[Dict[str, Any]]:
        """Get all projects

        API endpoint: GET /projects

        :param all_details: retrieve all project details (optional))
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the projects ("name,desc"; "name,asc")
        :type sort: str
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """

        full_url = self.url + "resource/api/projects"
        if all_details:
            full_url = self._add_param(full_url, "allDetails=true")

        if page > -1:
            full_url = self._add_param(full_url, "page=" + str(page))
            full_url = self._add_param(full_url, "page_entries=" + str(page_size))

        if sort:
            # ensure HTML encoding
            sort = sort.replace(",", "%2C")
            full_url = self._add_param(full_url, "sort=" + sort)

        resp = self.api_get(full_url)
        return resp

    def get_projects_by_type(self, project_type: str) -> List[Dict[str, Any]]:
        """Get information of about all projects of a certain type

        API endpoint: GET /projects

        :param project_type: the full url of the project to be requested
        :type project_type: string, one of CUSTOMER, INTERNAL, PRODUCT, SERVICE, INNER_SOURCE
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/projects?type=" + project_type)
        if not resp:
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:projects" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:projects"]

    def get_project_names(self) -> List[str]:
        """Get all project names

        API endpoint: GET /projects

        :return: JSON data
        :rtype: JSON
        :raises SW360Error: if there is a negative HTTP response
        """
        all_projects = self.get_projects()
        resp: List[str] = []
        if not all_projects:
            return resp

        if "_embedded" not in all_projects:
            return resp

        if "sw360:projects" not in all_projects["_embedded"]:
            return resp

        projects: List[Dict[str, Any]] = all_projects["_embedded"]["sw360:projects"]
        if not projects:
            return resp

        for key in projects:
            resp.append(key["name"] + ", " + key["version"])

        return resp

    def get_projects_by_name(self, name: str) -> List[Dict[str, Any]]:
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
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:projects" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:projects"]

    def get_projects_by_external_id(self, ext_id_name: str, ext_id_value: str = "") -> List[Dict[str, Any]]:
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
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:projects" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:projects"]

    def get_projects_by_group(self, group: str, all_details: bool = False) -> List[Dict[str, Any]]:
        """Get projects by group.

        API endpoint: GET /projects?group=

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
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:projects" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:projects"]

    def get_projects_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get projects by tag.

        API endpoint: GET /projects?tag=

        :param group: the group the projects shall belong to
        :type group: string
        :return: list of projects
        :rtype: list of JSON project objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/projects?tag=" + tag + "&luceneSearch=true"
        resp = self.api_get(full_url)
        if not resp:
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:projects" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:projects"]

    def get_project_vulnerabilities(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def create_new_project(self, name: str, project_type: str, visibility: Any,
                           description: str = "", version: str = "",
                           project_details: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
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

    def update_project(self, project: Dict[str, Any], project_id: str,
                       add_subprojects: bool = False) -> Optional[Dict[str, Any]]:
        """Update an existing project

        API endpoint: PATCH /projects

        :param project: the new project data
        :param project_id: the id of the project to be deleted
        :param add_subprojects: optional parameter only to add new sub-projects
        :type project: JSON
        :type project_id: string
        :type add_subprojects: bool
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        url = self.url + "resource/api/projects/" + project_id

        if add_subprojects:
            current = self.get_project(project_id)
            if (current is not None and "linkedProjects" in current and "linkedProjects" in project):
                for sp in current["linkedProjects"]:
                    pid = self.get_id_from_href(sp["project"])
                    if pid not in project["linkedProjects"]:
                        nsp = {}
                        nsp["projectRelationship"] = sp.get("relation", "CONTAINED")
                        project["linkedProjects"][pid] = nsp

        response = requests.patch(url, json=project, headers=self.api_headers)

        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_project_releases(self, releases: List[Dict[str, Any]], project_id: str, add: bool = False) -> bool:
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

    def update_project_external_id(self, ext_id_name: str, ext_id_value: str,
                                   project_id: str, update_mode: str = "none") -> Any:
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
        if not complete_data:
            return

        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_project(data, project_id)
        return old_value

    def delete_project(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def get_users_of_project(self, project_id: str) -> Optional[Dict[str, Any]]:
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

    def duplicate_project(self, project_id: str, new_version: str) -> Optional[Dict[str, Any]]:
        """Create a copy of an exisiting project.

        API endpoint: GET /projects/duplicate/{id}

        :param project_id: the id of the exisiting project
        :type project_id: string
        :param new_version: the version of the new project
        :type new_version: string
        :return: the newly created project
        :rtype: JSON object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not project_id:
            raise SW360Error(message="No project id provided!")

        project_details = {}
        project_details["version"] = new_version
        # force clearing state to OPEN
        project_details["clearingState"] = "OPEN"

        url = self.url + "resource/api/projects/duplicate/" + project_id
        response = requests.post(
            url, json=project_details, headers=self.api_headers
        )

        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_project_release_relationship(
        self, project_id: str, release_id: str, new_state: str,
            new_relation: str, comment: str) -> Optional[Dict[str, Any]]:
        """Update the relationship for a specific release of a project

        API endpoint PATCH /projects/{pid}/release{rid}

        :param project_id: the id of the exisiting project
        :type project_id: string
        :param release_id: the id of the release to be requested
        :type release_id: string
        :param new_state: the new mainline state of the release, one of
         (OPEN, MAINLINE, SPECIFIC, PHASEOUT, DENIED)
        :type new_state: string
        :param new_relation: the new relation of the release, one of
         (CONTAINED, REFERRED, UNKNOWN, DYNAMICALLY_LINKED, STATICALLY_LINKED, SIDE_BY_SIDE,
         STANDALONE, INTERNAL_USE, OPTIONAL, TO_BE_REPLACED, CODE_SNIPPET)
        :type new_relation: string
        :param comment: a comment
        :type comment: string
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        if not release_id:
            raise SW360Error(message="No release id provided!")

        relation = {}
        relation["releaseRelation"] = new_relation
        relation["mainlineState"] = new_state
        relation["comment"] = comment

        url = self.url + "resource/api/projects/" + project_id + "/release/" + release_id
        response = requests.patch(url, json=relation, headers=self.api_headers)

        if response.ok:
            return response.json()

        raise SW360Error(response, url)
