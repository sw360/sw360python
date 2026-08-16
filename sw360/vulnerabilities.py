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

from typing import Any, Dict, Optional

from .base import BaseMixin
from .sorting import SortParam, VulnerabilitySortColumn


class VulnerabilitiesMixin(BaseMixin):
    def get_all_vulnerabilities(
        self, search_text: str = "", all_details: bool = False,
        page: int = 0, page_size: int = 10, sort: Optional[SortParam] = None
    ) -> Optional[Dict[str, Any]]:
        """Get information of about all vulnerabilities

        API endpoint: GET /vulnerabilities

        :param search_text: filter by externalId or title of vulnerability,
        empty to get all
        :type search_text: string
        :param all_details: return all details about vulnerabilities (
        including releases)
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the vulnerabilities (Sort by last update if
        `None`)
        :type sort: SortParam
        :return: list of vulnerabilities
        :rtype: list of JSON vulnerability objects
        :raises SW360Error: if there is a negative HTTP response
        """
        fullbase_url = self.url + "resource/api/vulnerabilities"
        params = {}

        if search_text != "":
            params["search"] = search_text

        if all_details:
            params["allDetails"] = "true"

        if sort is None:
            sort = VulnerabilitySortColumn.LAST_UPDATE_DATE.desc()

        full_url = self._add_params(fullbase_url, params)
        if page > -1 and page_size > -1:
            full_url = self._add_pagination(full_url, page, page_size, sort)

        if self.is_above_version_18() and page_size == -1:
            resp = self.api_get_all(full_url, sort)
        else:
            resp = self.api_get(full_url)

        return resp

    def get_vulnerability(self, vulnerability_id: str) -> Optional[Dict[str, Any]]:
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
