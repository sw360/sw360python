# -------------------------------------------------------------------------------
# Copyright (c) 2019-2025 Siemens
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


class VendorMixin(BaseMixin):
    def get_all_vendors(self) -> List[Dict[str, Any]]:
        """Returns all vendors

        API endpoint: GET /vendors

        :return: a vendor
        :rtype: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vendors")
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

        resp = self.api_get(self.url + "resource/api/vendors/" + vendor_id)
        return resp

    def create_new_vendor(self, vendor: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new vendor

        API endpoint: POST /vendors

        :param vendor: the new vedor data
        :type vendor: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/vendors"
        response = self.api_post(
            url, json=vendor)
        if response is not None:
            if response.ok:
                return response.json()
        raise SW360Error(response, url)

    def update_vendor(self, vendor: Dict[str, Any], vendor_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing vendor

        API endpoint: PATCH /vendors

        :param vendor_id: the id of the vendor to be updated
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        # 2019-04-03: error 405 - not allowed

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id
        return self.api_patch(url, json=vendor)

    def delete_vendor(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Delete an existing vendor

        API endpoint: DELETE /vendors

        :param vendor_id: the id of the vendor
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        # 2019-04-03/2025-01-23: error 405 - not allowed

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id

        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                if response.text:
                    return response.json()

        return None
