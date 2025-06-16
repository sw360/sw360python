# -------------------------------------------------------------------------------
# Copyright (c) 2024 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

from typing import Any, Dict, Optional

from .base import BaseMixin


class ModerationRequestMixin(BaseMixin):
    def get_all_moderation_requests(self, page: int = -1, page_size: int = -1,
                                    sort: str = "") -> Optional[Dict[str, Any]]:
        """Get information of about all moderation requests

        API endpoint: GET /moderationrequest

        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the packages ("name,desc"; "name,asc")
        :type sort: str
        :return: list of moderation requests
        :rtype: list of JSON moderation requests objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/moderationrequest"
        params = {}

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)
        return resp

    def get_moderation_requests_by_state(self, state: str, all_details: bool = False,
                                         page: int = -1, page_size: int = -1,
                                         sort: str = "") -> Optional[Dict[str, Any]]:
        """Get information of about all moderation requests

        API endpoint: GET /moderationrequest/byState

        :param all_details: retrieve all package details (optional))
        :type all_details: bool
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the packages ("name,desc"; "name,asc")
        :type sort: str
        :return: list of moderation requests
        :rtype: list of JSON moderation requests objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/moderationrequest/byState"
        params = {"state": state}
        
        if all_details:
            params["allDetails"] = "true"

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)
        return resp
        
    def get_moderation_request(self, mr_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a moderation request

        API endpoint: GET /moderationrequest/{id}

        :param mr_id: the id of the moderation request to be requested
        :type mr_id: string
        :return: a moderation request
        :rtype: JSON moderation request object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/moderationrequest/" + mr_id)
        return resp
