# -------------------------------------------------------------------------------
# Copyright (c) 2019-2022 Siemens
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


class LicenseMixin(BaseMixin):
    def create_new_license(
        self,
        shortName: str,
        fullName: str,
        text: str,
        checked: bool = False,
        license_details: Dict[str, Any] = {},
    ) -> Any:
        """Create a new license

        API endpoint: POST /licenses

        :param shortName: short license name. i.e "MIT"
        :param fullName: descriptive license name
        :param text: license text
        :param checked: if license is checked
        :type shortname: string
        :type fullname: string
        :type text: string
        :type checked: bool
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/licenses"

        license_details["shortName"] = shortName
        license_details["fullName"] = fullName
        license_details["text"] = text
        license_details["checked"] = checked

        response = self.api_post(url, json=license_details)
        if response is not None:
            if response.ok:
                return response.json()
        raise SW360Error(response, url)

    def delete_license(self, license_shortname: str) -> Optional[bool]:
        """Delete an existing license

        API endpoint: PATCH /licenses

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

        resp = self.api_get(self.url + "resource/api/licenses")
        if not resp:
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:licenses" not in resp["_embedded"]:
            return []

        return resp["_embedded"]["sw360:licenses"]

    def get_license(self, license_id: str) -> Optional[Dict[str, Any]]:
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
