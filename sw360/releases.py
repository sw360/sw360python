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

from .base import BaseMixin
from .sw360error import SW360Error


class ReleasesMixin(BaseMixin):
    def get_release(self, release_id: str) -> Optional[Dict[str, Any]]:
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

    def get_release_by_url(self, release_url: str) -> Optional[Dict[str, Any]]:
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

    def get_releases_by_name(self, name: str) -> List[Any]:
        """Gets a list of releases that match the given name.

        API endpoint: GET /releases?name=

        :param name: the name
        :type name: string
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/releases?name=" + name
        resp = self.api_get(full_url)
        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            return resp["_embedded"]["sw360:releases"]

        return []

    # return type List[Dict[str, Any]] | Optional[Dict[str, Any]] for Python 3.11 is good,
    # Union[List[Dict[str, Any]], Optional[Dict[str, Any]]] for lower Python versions is not good
    def get_all_releases(self, fields: str = "", all_details: bool = False, page: int = -1,
                         page_size: int = -1, sort: str = "") -> Any:
        """Get information of about all releases

        API endpoint: GET /releases

        :param all_details: retrieve all project details (optional))
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the releases ("name,desc"; "name,asc")
        :type sort: str
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/releases"
        if all_details:
            full_url = self._add_param(full_url, "allDetails=true")

        if fields:
            full_url = self._add_param(full_url, "fields=" + fields)

        if page > -1:
            full_url = self._add_param(full_url, "page=" + str(page))
            full_url = self._add_param(full_url, "page_entries=" + str(page_size))

        if sort:
            # ensure HTML encoding
            sort = sort.replace(",", "%2C")
            full_url = self._add_param(full_url, "sort=" + sort)

        resp = self.api_get(full_url)

        if page == -1 and resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            return resp["_embedded"]["sw360:releases"]

        return resp

    def get_releases_by_external_id(self, ext_id_name: str, ext_id_value: str = "") -> List[Dict[str, Any]]:
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
            return resp["_embedded"]["sw360:releases"]

        return []

    def create_new_release(self, name: str, version: str, component_id: str,
                           release_details: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
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
        response = self.api_post(
            url, json=release_details)
        if response is not None:
            if response.ok:
                return response.json()
        return None

    def update_release(self, release: Dict[str, Any], release_id: str) -> Optional[Dict[str, Any]]:
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
        return self.api_patch(url, json=release)

    def update_release_external_id(self, ext_id_name: str, ext_id_value: str,
                                   release_id: str, update_mode: str = "none") -> Optional[Dict[str, Any]]:
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
        if complete_data:
            ret = self._update_external_ids(complete_data, ext_id_name,
                                            ext_id_value, update_mode)
            (old_value, data, update) = ret
            if update:
                self.update_release(data, release_id)
            return old_value

        return {}

    def delete_release(self, release_id: str) -> Optional[Dict[str, Any]]:
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
        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                return response.json()
        return None

    def get_users_of_release(self, release_id: str) -> Optional[Dict[str, Any]]:
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

    def link_packages_to_release(self, release_id: str, packages: List[str]) -> Optional[Dict[str, Any]]:
        """Link (new) packages to a given release.

        API endpoint PATCH /release/{pid}/packages{rid}

        :param release_id: the id of the existing release
        :type release_id: string
        :param packages: list of package ids
        :type packages: list of string
        :rtype: JSON SW360 result object
        :raises SW360Error: if the release id is missing ir there is a negative HTTP response
        """
        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id + "/link/packages/"
        return self.api_patch(url, json=packages)

    def unlink_packages_from_release(self, release_id: str, packages: List[str]) -> Optional[Dict[str, Any]]:
        """Unlink packages from a given release.

        API endpoint PATCH /release/{pid}/packages{rid}

        :param release_id: the id of the existing release
        :type release_id: string
        :param packages: list of package ids
        :type packages: list of string
        :rtype: JSON SW360 result object
        :raises SW360Error: if the project id is missing ir there is a negative HTTP response
        """
        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id + "/unlink/packages/"
        return self.api_patch(url, json=packages)
