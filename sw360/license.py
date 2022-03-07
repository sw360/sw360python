# -------------------------------------------------------------------------------
# (c) 2019-2022 Siemens AG
# (c) 2022 BMW CarIT GmbH
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
# Authors: helio.chissini-de-castro@bmw.de
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import requests


class LicenseMixin:
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

        if "_embedded" not in resp:
            return None

        if "sw360:licenses" not in resp["_embedded"]:
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
