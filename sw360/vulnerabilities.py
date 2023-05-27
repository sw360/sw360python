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

class VulnerabilitiesMixin:
    def get_all_vulnerabilities(self):
        """Get information of about all vulnerabilities

        API endpoint: GET /vulnerabilities

        :return: list of vulnerabilities
        :rtype: list of JSON vulnerability objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/vulnerabilities")
        return resp

    def get_vulnerability(self, vulnerability_id):
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
