# -------------------------------------------------------------------------------
# Copyright (c) 2024-2026 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, mishra.gaurav@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional

from .base import BaseMixin
from .sorting import PackageSortColumn, SortParam
from .sw360error import SW360Error


class PackagesMixin(BaseMixin):

    def __get_packages_filtered(
        self, url: str, page: int = -1, page_size: int = -1,
        sort: Optional[SortParam] = None
    ) -> Any:
        """
        Take a pre-generated URL of packages endpoint, with filters applied.
        Then call the API with appropriate pagination and sorting to get the
        packages.

        :param url: Packages API URL with filters in the query
        :type url: str
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the package
        :type sort: SortParam
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """

        if self.is_above_version_18():
            full_url = self._add_params(url, {"luceneSearch": "true"})
        else:
            full_url = url

        if page > -1 and page_size > -1:
            full_url = self._add_pagination(full_url, page, page_size, sort)

        if self.is_above_version_18() and page_size == -1:
            resp = self.api_get_all(full_url, sort)
        else:
            resp = self.api_get(full_url)

        if (resp and
            "_embedded" in resp and
                "sw360:packages" in resp["_embedded"]):
            return resp["_embedded"]["sw360:packages"]

        return []

    def get_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a package

        API endpoint: GET /package/{id}

        :param package_id: the id of the package to be requested
        :type package_id: string
        :return: a package
        :rtype: JSON package object
        :raises SW360Error: if there is a negative HTTP response
        """
        if not package_id:
            raise SW360Error(message="No package id provided!")

        resp = self.api_get(self.url + "resource/api/packages/" + package_id)
        return resp

    def get_packages_by_name(
        self, name: str, page: int = -1, page_size: int = -1,
        sort: Optional[SortParam] = None
    ) -> List[Any]:
        """Gets a list of packages that match the given name.

        API endpoint: GET /packages?name=

        :param name: the name
        :type name: string
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the packages (Sort by score if `None`)
        :type sort: SortParam
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not name:
            raise SW360Error(message="No package name provided!")

        fullbase_url = self.url + "resource/api/packages"
        params = {"name": name}

        url_with_param = self._add_params(fullbase_url, params)

        if sort is None:
            if self.is_above_version_18():
                sort = PackageSortColumn.SCORE.asc()
            else:
                sort = PackageSortColumn.NAME.asc()

        return self.__get_packages_filtered(url_with_param, page, page_size, sort)

    def get_all_packages(
        self, name: str = "", version: str = "", purl: str = "",
        all_details: bool = False, page: int = -1, page_size: int = -1,
        sort: Optional[SortParam] = None
    ) -> Any:
        """Get information of about all packages

        API endpoint: GET /releases

        :param name: name to filter
        :type name: str
        :param version: version to filter
        :type version: str
        :param purl: purl to filter
        :type purl: str
        :param all_details: retrieve all package details (optional)
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the components (name default, score if
        filtering)
        :type sort: SortParam
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
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

        url_with_param = self._add_params(fullbase_url, params)

        if sort is None:
            sort = PackageSortColumn.NAME.asc()
            if name != "" or version != "" or purl != "":
                if self.is_above_version_18():
                    sort = PackageSortColumn.SCORE.asc()
                else:
                    sort = PackageSortColumn.NAME.asc()

        return self.__get_packages_filtered(url_with_param, page, page_size,
                                            sort)

    def get_packages_by_packagemanager(
        self, manager: str, page: int = -1, page_size: int = -1,
        sort: Optional[SortParam] = None
    ) -> Any:
        """Get information of about all packages of a specific package manager

        API endpoint: GET /releases?packageManager=

        :param manager: name of the package manager
        :type manager: str
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the components (Sort by score if `None`)
        :type sort: SortParam
        :return: list of packages
        :rtype: list of JSON package objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not manager:
            raise SW360Error(message="No package manager provided!")

        fullbase_url = self.url + "resource/api/packages"
        params = {"packageManager": manager}

        url_with_param = self._add_params(fullbase_url, params)

        if sort is None:
            if self.is_above_version_18():
                sort = PackageSortColumn.SCORE.asc()
            else:
                sort = PackageSortColumn.NAME.asc()

        return self.__get_packages_filtered(url_with_param, page, page_size,
                                            sort)

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
        if not name:
            raise SW360Error(message="No package name provided!")

        if not version:
            raise SW360Error(message="No package version provided!")

        if not purl:
            raise SW360Error(message="No package purl provided!")

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

        API endpoint: PATCH /packages/{id}

        :param package: the new package data
        :param package_id: the id of the package to be updated
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

        API endpoint: DELETE /packages/{id}

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

    def get_users_of_package(self, package_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about the uses of a package

        API endpoint: GET /packages/{id}/usage

        :param package_id: the id of the package to be requested
        :type package_id: string
        :return: all uses of this package
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not package_id:
            raise SW360Error(message="No package id provided!")

        resp = self.api_get(self.url + "resource/api/packages/" + package_id
                            + "/usage")
        return resp
