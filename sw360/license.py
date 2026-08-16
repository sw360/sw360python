# -------------------------------------------------------------------------------
# Copyright (c) 2019-2026 Siemens
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
from .sorting import LicenseSortColumn
from .sw360error import SW360Error


class LicenseMixin(BaseMixin):
    def create_new_license(
        self,
        shortName: str,
        fullName: str,
        text: str,
        checked: bool = False,
    ) -> Any:
        """Create a new license

        API endpoint: POST /licenses

        :param shortName: short license name. i.e "MIT"
        :param fullName: descriptive license name
        :param text: license text
        :param checked: if license is checked
        :type shortName: string
        :type fullName: string
        :type text: string
        :type checked: bool
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """
        if not shortName:
            raise SW360Error(message="No short name provided!")

        if not fullName:
            raise SW360Error(message="No full name provided!")

        if not text:
            raise SW360Error(message="No license text provided!")

        url = self.url + "resource/api/licenses"

        license_details = {
            "shortName": shortName,
            "fullName": fullName,
            "text": text,
            "checked": checked,
        }

        response = self.api_post(url, json=license_details)
        if response is not None:
            if response.ok:
                return response.json()
        raise SW360Error(response, url)

    def delete_license(self, license_shortname: str) -> Optional[bool]:
        """Delete an existing license

        API endpoint: DELETE /licenses

        :param license_shortname: license shortname as the id
        :type license_shortname: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not license_shortname:
            raise SW360Error(message="No license shortname provided!")

        url = self.url + "resource/api/licenses/" + license_shortname
        print(url)
        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                return True
        return None

    def download_license_info(
        self, project_id: str, filename: str, generator: str = "XhtmlGenerator", variant: str = "DISCLOSURE"
    ) -> None:
        """Gets the license information, aka Readme_OSS for the project
        with the given id

        API endpoint: GET /projects

        :param project_id: the id of the project to be deleted
        :param filename: the filename to be used
        :type project_id: string
        :type filename: string
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        if not filename:
            raise SW360Error(message="No filename provided!")

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        url = (
            self.url
            + "resource/api/projects/"
            + project_id
            + "/licenseinfo?generatorClassName="
            + generator
            + "&variant="
            + variant
        )
        req = requests.get(url, allow_redirects=True, headers=hdr)
        open(filename, "wb").write(req.content)

    def get_all_licenses(self) -> List[Dict[str, Any]]:
        """Get information of about all licenses

        API endpoint: GET /licenses

        :return: list of licenses
        :rtype: list of JSON license objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/licenses"
        sort = LicenseSortColumn.SHORT_NAME.asc()

        if self.is_above_version_18():
            resp = self.api_get_all(fullbase_url)
        else:
            resp = self.api_get(fullbase_url)

        if resp and "_embedded" in resp and "sw360:licenses" in resp["_embedded"]:
            return resp["_embedded"]["sw360:licenses"]

        return []

    def get_license(self, license_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a license

        API endpoint: GET /licenses/{id}

        :param license_id: the id of the license to be requested
        :type license_id: string
        :return: a license
        :rtype: JSON license object
        :raises SW360Error: if there is a negative HTTP response
        """
        if not license_id:
            raise SW360Error(message="No license id provided!")

        resp = self.api_get(self.url + "resource/api/licenses/" + license_id)
        return resp

    def search_license(self, search_text: str) -> Optional[Dict[str, Any]]:
        """Get search a license by fullName, shortName or text

        API endpoint: GET /licenses?searchText=

        :param search_text: the search string
        :type search_text: string
        :return: list of licenses
        :rtype: list of JSON license objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not search_text:
            raise SW360Error(message="Search Text provided!")

        fullbase_url = self.url + "resource/api/licenses"
        params = {"searchText": search_text}
        full_url = self._add_params(fullbase_url, params)

        sort = LicenseSortColumn.SCORE.asc()

        resp = self.api_get_all(full_url, sort)
        return resp
