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

import requests

from .sw360error import SW360Error


class VendorMixin:
    def get_all_vendors(self):
        """Returns all vendors

        API endpoint: GET /vendors

        :return: a vendor
        :rtype: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vendors")
        if not resp:
            return None

        if "_embedded" not in resp:
            return None

        if "sw360:vendors" not in resp["_embedded"]:
            return None

        resp = resp["_embedded"]["sw360:vendors"]
        return resp

    def get_vendor(self, vendor_id):
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

    def create_new_vendor(self, vendor):
        """Create a new vendor

        API endpoint: POST /vendors

        :param vendor: the new vedor data
        :type vendor: JSON vendor object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/vendors"
        response = requests.post(
            url, json=vendor, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_vendor(self, vendor, vendor_id):
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
        response = requests.patch(
            url, json=vendor, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def delete_vendor(self, vendor_id):
        """Delete an existing vendor

        API endpoint: DELETE /vendors

        :param vendor_id: the id of the vendor
        :type vendor_id: string
        :raises SW360Error: if there is a negative HTTP response
        """

        # 2019-04-03: error 405 - not allowed

        if not vendor_id:
            raise SW360Error(message="No vendor id provided!")

        url = self.url + "resource/api/vendors/" + vendor_id
        response = requests.delete(
            url, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)
