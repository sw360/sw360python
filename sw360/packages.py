# -------------------------------------------------------------------------------
# Copyright (c) 2024-2025 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional

from .base import BaseMixin
from .sw360error import SW360Error


class PackagesMixin(BaseMixin):
    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a package

        API endpoint: GET /package/{id}

        :param package_id: the id of the package to be requested
        :type package_id: string
        :return: a package
        :rtype: JSON package object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/packages/" + package_id)
        return resp

    def get_packages_by_name(self, name: str) -> List[Any]:
        """Gets a list of packages that match the given name.

        API endpoint: GET /packages?name=

        :param name: the name
        :type name: string
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/packages?name=" + name
        resp = self.api_get(full_url)
        if resp and ("_embedded" in resp) and ("sw360:packages" in resp["_embedded"]):
            return resp["_embedded"]["sw360:packages"]

        return []

    def get_all_packages(self, name: str = "", version: str = "", purl: str = "",
                         all_details: bool = False, page: int = -1,
                         page_size: int = -1, sort: str = "") -> Any:
        """Get information of about all packages

        API endpoint: GET /releases

        :param all_details: retrieve all package details (optional))
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the packages ("name,desc"; "name,asc")
        :type sort: str
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """
        fullbase_url = self.url + "resource/api/packages"
        params = {}

        if all_details:
            params["allDetails"] = "true"

        if name:
            params["name"] = name

        if version:
            params["version"] = version

        if purl:
            params["purl"] = purl

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)

        if page == -1 and resp and ("_embedded" in resp) and ("sw360:packages" in resp["_embedded"]):
            return resp["_embedded"]["sw360:packages"]

        return resp

    def get_packages_by_packagemanager(self, manager: str, page: int = -1,
                                       page_size: int = -1, sort: str = "") -> Any:
        """Get information of about all packages of a specific package manager

        API endpoint: GET /releases

        :param manager: name of the package manager
        :type manager: str
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the packages ("name,desc"; "name,asc")
        :type sort: str
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """
        fullbase_url = self.url + "resource/api/packages"
        params = {"packageManager": manager}

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)

        if page == -1 and resp and ("_embedded" in resp) and ("sw360:packages" in resp["_embedded"]):
            return resp["_embedded"]["sw360:packages"]

        return resp

    def create_new_package(self, name: str, version: str, purl: str,
                           package_type: str, package_details: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
        """Create a new package

        API endpoint: POST /packages

        :param name: name of new package (usually set to component name)
        :param version: version string of new package (e.g. "1.0")
        :param purl: purl / package-url of the package
        :param package_type: CycloneDX package type of the package
        :param package_details: further package details as defined by SW360 REST API
        :type name: string
        :type version: string
        :type purl: string
        :type package_type: string
        :type package_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        for param in "name", "version":
            package_details[param] = locals()[param]
        package_details["purl"] = purl
        package_details["packageType"] = package_type

        url = self.url + "resource/api/packages"
        response = self.api_post(
            url, json=package_details)
        if response is not None:
            if response.ok:
                return response.json()
        return None

    def update_package(self, package: Dict[str, Any], package_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing package

        API endpoint: PATCH /packages

        :param release: the new package data
        :param release_id: the id of the package to be updated
        :type package: JSON
        :type package_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not package_id:
            raise SW360Error(message="No package id provided!")

        url = self.url + "resource/api/packages/" + package_id
        return self.api_patch(url, json=package)

    def delete_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Delete an existing package

        API endpoint: DELETE /packages

        :param package_id: the id of the package to be deleted
        :type package_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not package_id:
            raise SW360Error(message="No package id provided!")

        url = self.url + "resource/api/packages/" + package_id
        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                if response.text:
                    return response.json()
        return None
