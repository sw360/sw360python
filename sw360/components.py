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


class ComponentsMixin(BaseMixin):
    # return type List[Dict[str, Any]] | Optional[Dict[str, Any]] for Python 3.11 is good,
    # Union[List[Dict[str, Any]], Optional[Dict[str, Any]]] for lower Python versions is not good
    def get_all_components(self, fields: str = "", page: int = -1, page_size: int = -1,
                           all_details: bool = False,
                           sort: str = "") -> Any:
        """Get information of about all components

        API endpoint: GET /components

        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param all_details: retrieve all component details (optional))
        :type all_details: bool
        :param sort: sort order for the components ("name,desc"; "name,asc")
        :type sort: str
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/components"
        params = {}

        if all_details:
            params["allDetails"] = "true"

        if fields:
            params["fields"] = fields

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)
        if not resp:
            return []

        if "_embedded" not in resp:
            return []

        if "sw360:components" not in resp["_embedded"]:
            return []

        if page == -1:
            return resp["_embedded"]["sw360:components"]

        return resp

    def get_components_by_type(
            self,
            component_type: str,
            page: int = -1,
            page_size: int = -1,
            sort: str = "") -> List[Dict[str, Any]]:
        """Get information of about all components for certain type

        API endpoint: GET /components

        :param component_type: the type of the component to be requested, one
         of INTERNAL, OSS, COTS, FREESOFTWARE, INNER_SOURCE, SERVICE
        :type component_type: string
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the components ("name,desc"; "name,asc")
        :type sort: str
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/components"
        params = {"type": component_type}

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)

        if resp and ("_embedded" in resp) and ("sw360:components" in resp["_embedded"]):
            return resp["_embedded"]["sw360:components"]

        return []

    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about a component

        API endpoint: GET /components/{id}

        :param component_id: the id of the component to be requested
        :type component_id: string
        :return: a component
        :rtype: JSON component object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components/" + component_id)
        return resp

    def get_component_by_url(self, component_url: str) -> Optional[Dict[str, Any]]:
        """Get information of about a component

        API endpoint: GET /components

        :param url: the full url of the component to be requested
        :type url: string
        :return: a component
        :rtype: JSON component object
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(component_url)
        return resp

    def get_component_by_name(
            self,
            component_name: str,
            page: int = -1,
            page_size: int = -1,
            sort: str = "") -> Optional[Dict[str, Any]]:
        """Get information of about a component

        API endpoint: GET /components

        :param component_name: the name of the component to look for
        :type component_name: string
        :param page: page to retrieve
        :type page: int
        :param page_size: page size to use
        :type page_size: int
        :param sort: sort order for the components ("name,desc"; "name,asc")
        :type sort: str
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        fullbase_url = self.url + "resource/api/components"
        params = {"name": component_name}

        if page > -1:
            params["page"] = str(page)
            params["page_entries"] = str(page_size)

        if sort:
            params["sort"] = sort

        full_url = self._add_params(fullbase_url, params)
        resp = self.api_get(full_url)
        return resp

    def get_components_by_external_id(self, ext_id_name: str, ext_id_value: str = "") -> List[Dict[str, Any]]:
        """Get components by external id. `ext_id_value` can be left blank to
        search for all components with `ext_id_name`.

        API endpoint: GET /components

        :param ext_id_name: the name of the external id to look for
        :param ext_id_value: the value of the external id to look for
        :type ext_id_name: string
        :type ext_id_value: string
        :return: list of components
        :rtype: list of JSON component objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(
            self.url
            + "resource/api/components/searchByExternalIds?"
            + ext_id_name
            + "="
            + ext_id_value
        )
        if resp and ("_embedded" in resp) and ("sw360:components" in resp["_embedded"]):
            return resp["_embedded"]["sw360:components"]

        return []

    def create_new_component(self, name: str, description: str, component_type: str, homepage: str,
                             component_details: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
        """Create a new component

        API endpoint: POST /components

        :param name: name of the new component
        :param description: description of the new component
        :param component_type: type of the new component, one of
         "INTERNAL", "OSS", "COTS", "FREESOFTWARE", "INNER_SOURCE", "SERVICE", "CODE_SNIPPET"
        :param homepage: homepage url of the new component
        :param component_details: further component details as defined by SW360 REST API
        :type name: string
        :type description: string
        :type component_type: string
        :type homepage: string
        :type component_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        url = self.url + "resource/api/components"

        for param in "name", "description", "homepage":
            component_details[param] = locals()[param]
        component_details["componentType"] = component_type

        response = self.api_post(
            url, json=component_details)
        if response is not None:
            if response.ok:
                return response.json()
        return None

    def update_component(self, component: Dict[str, Any], component_id: str) -> Optional[Dict[str, Any]]:
        """Update an existing component

        API endpoint: PATCH /components

        :param component: the new component data
        :param component_id: the id of the component to be updated
        :type component: JSON component object
        :type component_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not component_id:
            raise SW360Error(message="No component id provided!")

        url = self.url + "resource/api/components/" + component_id
        return self.api_patch(url, json=component)

    def update_component_external_id(self, ext_id_name: str, ext_id_value: str,
                                     component_id: str, update_mode: str = "none") -> Optional[Dict[str, Any]]:
        """Set or update external id of a component. If the id is already set, it
        will only be changed if `update_mode=="overwrite"`. The id can be
        deleted using `update_mode=="delete"`.

        The method will return the old value of the external id or None if it
        was not set.

        API endpoint: PATCH /components

        :param ext_id_name: name of the external id
        :param ext_id_value: value of the external id
        :param component_id: the id of the component to be updated
        :param update_mode: can be "none" (default), "overwrite" or "delete"
        :type ext_id_name: string
        :type ext_id_value: string
        :type component_id: string
        :type update_mode: string
        :return: old value of external id
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        complete_data = self.get_component(component_id)
        if not complete_data:
            return None

        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_component(data, component_id)
        return old_value

    def delete_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Delete an existing component

        API endpoint: DELETE /components

        :param component_id: the id of the component to be deleted
        :type component_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not component_id:
            raise SW360Error(message="No component id provided!")

        url = self.url + "resource/api/components/" + component_id
        response = self.api_delete(url)
        if response is not None:
            if response.ok:
                if response.text:
                    return response.json()
        return None

    def get_users_of_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get information of about the users of a component

        API endpoint: GET /components/usedBy/{id}

        :param component_id: the id of the component to be requested
        :type component_id: string
        :return: all users of this component
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/components/usedBy/" + component_id)
        return resp

    def get_recent_components(self) -> Optional[List[Dict[str, Any]]]:
        """Get 5 of the service's most recently created components.

        API endpoint: GET /components/recentComponents

        :return: a list of components
        :rtype: JSON list of component objects
        :raises SW360Error: if there is a negative HTTP response
        """
        url = self.url + "resource/api/components/recentComponents"
        resp = self.api_get(url)
        if resp and ("_embedded" in resp) and ("sw360:components" in resp["_embedded"]):
            return resp["_embedded"]["sw360:components"]

        return []
