# -------------------------------------------------------------------------------
# Copyright (c) 2019-2023 Siemens
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


class ClearingMixin(BaseMixin):
    def get_clearing_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a clearing request

        API endpoint: GET /clearingrequest/{id}

        :param request_id: the id of the clearing request to be requested
        :type request_id: string
        :return: a clearing request
        :rtype: JSON clearing request object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/clearingrequest/" + request_id)
        return resp

    def get_clearing_request_for_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a clearing request for a specific project

        API endpoint: GET /clearingrequest/project/{id}

        :param request_id: the id of the clearing request to be requested
        :type request_id: string
        :return: a clearing request
        :rtype: JSON clearing request object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/clearingrequest/project/" + project_id)
        return resp
