# -------------------------------------------------------------------------------
# Copyright (c) 2026 Siemens
# All Rights Reserved.
# Authors: mishra.gaurav@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, List, Optional

import requests

from .base import BaseMixin
from .sw360error import SW360Error


class ReportsMixin(BaseMixin):
    def generate_project_license_info(
        self, project_id: str, filename: str, format: str = "HTML",
        with_subprojects: bool = False
    ) -> int:
        """Gets the license information, aka Readme_OSS for the project
        with the given id

        API endpoint: GET /reports

        :param project_id: ID of the Project to generate the report for
        :type project_id: string
        :param filename: the filename to be used
        :type filename: string
        :param format: the format of the report ("HTML", "DOCX" or "TEXT")
        :type format: string
        :param with_subprojects: whether to include subprojects in the report
        :type with_subprojects: bool
        :return: 1 if the file saved, 2 if the backend sent email instead
        :rtype: int
        :raises SW360Error: if there is a negative HTTP response
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        if not filename:
            raise SW360Error(message="No filename provided!")

        generator_class_name = "XhtmlGenerator"
        if format == "DOCX":
            generator_class_name = "DocxGenerator"
        elif format == "TEXT":
            generator_class_name = "TextGenerator"

        fullbase_url = self.url + "resource/api/reports"

        params = {
            "withlinkedreleases": "false",
            "projectId": project_id,
            "module": "licenseInfo",
            "generatorClassName": generator_class_name,
            "variant": "DISCLOSURE",
        }
        if with_subprojects:
            params["withSubProject"] = "true"
        else:
            params["withSubProject"] = "false"

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        url = self._add_params(fullbase_url, params)
        resp = requests.get(url, allow_redirects=True, headers=hdr)
        if not resp.ok:
            raise SW360Error(resp, url, "LicenseInfo generation failed")

        return_status = 1
        if "Content-Disposition" in resp.headers:
            # Report in the response, save to file
            with open(filename, "wb") as report:
                report.write(resp.content)
        else:
            return_status = 2
        return return_status

    def generate_project_clearing_report(
        self, project_id: str, filename: str, with_subprojects: bool = False
    ) -> int:
        """Gets the clearing report, aka Product Clearing for the project
        with the given id

        API endpoint: GET /reports

        :param project_id: ID of the Project to generate the report for
        :type project_id: string
        :param filename: the filename to be used
        :type filename: string
        :param with_subprojects: whether to include subprojects in the report
        :type with_subprojects: bool
        :return: 1 if the file saved, 2 if the backend sent email instead
        :rtype: int
        :raises SW360Error: if there is a negative HTTP response
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        if not filename:
            raise SW360Error(message="No filename provided!")

        fullbase_url = self.url + "resource/api/reports"

        params = {
            "withlinkedreleases": "false",
            "projectId": project_id,
            "module": "licenseInfo",
            "generatorClassName": "DocxGenerator",
            "variant": "REPORT",
        }
        if with_subprojects:
            params["withSubProject"] = "true"
        else:
            params["withSubProject"] = "false"

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        url = self._add_params(fullbase_url, params)
        resp = requests.get(url, allow_redirects=True, headers=hdr)
        if not resp.ok:
            raise SW360Error(resp, url, "Clearing Report generation failed")

        return_status = 1
        if "Content-Disposition" in resp.headers:
            # Report in the response, save to file
            with open(filename, "wb") as report:
                report.write(resp.content)
        else:
            return_status = 2
        return return_status

    def generate_project_source_code_bundle(
        self, project_id: str, filename: str, with_subprojects: bool = False
    ) -> None:
        """Save the source code bundle for the project with the given id

        API endpoint: GET /reports

        :param project_id: ID of the Project to generate the report for
        :type project_id: string
        :param filename: the filename to be used, must end with `.zip`
        :type filename: string
        :param with_subprojects: whether to include subprojects in the report
        :type with_subprojects: bool
        :raises SW360Error: if there is a negative HTTP response
        """
        if not project_id:
            raise SW360Error(message="No project id provided!")

        if not filename:
            raise SW360Error(message="No filename provided!")

        if not filename.endswith(".zip"):
            raise SW360Error(message="Filename must end with `.zip`")

        fullbase_url = self.url + "resource/api/reports"

        params = {
            "withlinkedreleases": "false",
            "projectId": project_id,
            "module": "licenseResourceBundle",
            "excludeReleaseVersion": "false",
        }
        if with_subprojects:
            params["withSubProject"] = "true"
        else:
            params["withSubProject"] = "false"

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        url = self._add_params(fullbase_url, params)
        resp = requests.get(url, allow_redirects=True, headers=hdr)
        if not resp.ok:
            raise SW360Error(resp, url, "Source Bundle generation failed")

        with open(filename, "wb") as report:
            report.write(resp.content)
