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

from .base import BaseMixin
from .sorting import SortParam, VendorSortColumn
from .sw360error import SW360Error


class VendorMixin(BaseMixin):
    def get_all_vendors(
        self, page: int = -1, page_size: int = -1, sort: Optional[SortParam] = None
    ) -> List[Dict[str, Any]]:
        """Returns all vendors

        API endpoint: GET /vendors

        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the vendors (Sort by name if `None`)
        :type sort: SortParam
        :return: list of vendors
        :rtype: list of JSON vendor objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/vendors"

        if sort is None:
            sort = VendorSortColumn.SHORT_NAME.asc()

        full_url = fullbase_url
        if page > -1 and page_size > -1:
            full_url = self._add_pagination(full_url, page, page_size, sort)

        if page_size == -1:
            resp = self.api_get_all(full_url, sort)
        else:
            resp = self.api_get(full_url)

        if resp and "_embedded" in resp and "sw360:vendors" in resp["_embedded"]:
            return resp["_embedded"]["sw360:vendors"]

        return []

    def search_vendors(
        self, search_text: str, page: int = -1, page_size: int = -1,
        sort: Optional[SortParam] = None
    ) -> List[Dict[str, Any]]:
        """Search vendors by full name or short name

        API endpoint: GET /vendors?searchText={search_text}

        :param search_text: search text
        :type search_text: string
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use, `-1` to get all
        :type page_size: int
        :param sort: sort order for the vendors (Sort by score if `None`)
        :type sort: SortParam
        :return: list of vendors
        :rtype: list of JSON vendor objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not search_text:
            raise SW360Error(message="No search text provided!")

        fullbase_url = self.url + "resource/api/vendors"
        params = {"searchText": search_text}

        if sort is None:
            sort = VendorSortColumn.SCORE.asc()

        full_url = self._add_params(fullbase_url, params)
        if page > -1 and page_size > -1:
            full_url = self._add_pagination(full_url, page, page_size, sort)

        if page_size == -1:
            resp = self.api_get_all(full_url, sort)
        else:
            resp = self.api_get(full_url)

        if resp and "_embedded" in resp and "sw360:vendors" in resp["_embedded"]:
            return resp["_embedded"]["sw360:vendors"]

        return []

    def get_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Returns a vendor

        API endpoint: GET /vendors/{id}

        :param vendor_id: the id of the vendor to be requested
        :type vendor_id: string
        :return: list of vendors
        :rtype: list of JSON vendor objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        resp = self.api_get(self.url + "resource/api/vendors/" + vendor_id)
        return resp

    def create_new_vendor(self, vendor: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new vendor

        API endpoint: POST /vendors

        :param vendor: the new vendor data
        :type vendor: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """
        if not vendor:
            raise SW360Error(message="No vendor data provided!")

        url = self.url + "resource/api/vendors"
        response = self.api_post(
            url, json=vendor)
        if response is not None:
            if response.ok:
                return response.json()
        raise SW360Error(response, url)

    def update_vendor(self, vendor: Dict[str, Any], vendor_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing vendor

        API endpoint: PATCH /vendors/{id}

        :param vendor: the new vendor data
        :type vendor: JSON vendor object
        :param vendor_id: the id of the vendor to be updated
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id
        return self.api_patch(url, json=vendor)

    def delete_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Delete an existing vendor

        API endpoint: DELETE /vendors/{id}

        :param vendor_id: the id of the vendor
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id

        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                if response.text:
                    return response.json()

        return None

    def get_users_of_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about the releases supplied by the vendor

        API endpoint: GET /vendors/{id}/releases

        :param vendor_id: the id of the vendor to be requested
        :type vendor_id: string
        :return: all releases supplied by this vendor
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """
        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        resp = self.api_get(self.url + "resource/api/vendors/" + vendor_id + "/releases")
        return resp
