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

from .sw360error import SW360Error


class ReleasesMixin:
    def get_release(self, release_id):
        """Get information of about a release

        API endpoint: GET /releases/{id}

        :param release_id: the id of the release to be requested
        :type release_id: string
        :return: a release
        :rtype: JSON release object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(self.url + "resource/api/releases/" + release_id)
        return resp

    def get_release_by_url(self, release_url):
        """Get information of about a release

        API endpoint: GET /releases

        :param url: the full url of the release to be requested
        :type url: string
        :return: a release
        :rtype: JSON release object
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(release_url)
        return resp

    def get_releases_by_name(self, name):
        """Gets a list of releases that match the given name.

        API endpoint: GET /releases?name=

        :param name: the name
        :type name: string
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/releases?name=" + name
        resp = self.api_get(full_url)
        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:releases"]
        return resp

    def get_all_releases(self, fields=None, all_details=False):
        """Get information of about all releases

        API endpoint: GET /releases

        :param all_details: retrieve all project details (optional))
        :type all_details: bool
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        full_url = self.url + "resource/api/releases"
        if all_details:
            full_url = full_url + "?allDetails=true"

        if fields:
            full_url = full_url + "?fields=" + fields

        resp = self.api_get(full_url)

        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:releases"]
        return resp

    def get_releases_by_external_id(self, ext_id_name, ext_id_value=""):
        """Get releases by external id. `ext_id_value` can be left blank to
        search for all releases with `ext_id_name`.

        API endpoint: GET /releases

        :param ext_id_name: the name of the external id to look for
        :param ext_id_value: the value of the external id to look for
        :type ext_id_name: string
        :type ext_id_value: string
        :return: list of releases
        :rtype: list of JSON release objects
        :raises SW360Error: if there is a negative HTTP response
        """
        resp = self.api_get(
            self.url
            + "resource/api/releases/searchByExternalIds?"
            + ext_id_name + "=" + ext_id_value
        )
        if resp and ("_embedded" in resp) and ("sw360:releases" in resp["_embedded"]):
            resp = resp["_embedded"]["sw360:releases"]
        return resp

    def create_new_release(self, name, version, component_id, release_details={}):
        """Create a new release

        API endpoint: POST /releases

        :param name: name of new release (usually set to component name)
        :param version: version string of new release (e.g. "1.0")
        :param component_id: SW360 ID of component in which release shall be created
        :param release_details: further release details as defined by SW360 REST API
        :type name: string
        :type version: string
        :type component_id: string
        :type release_details: dict
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        for param in "name", "version":
            release_details[param] = locals()[param]
        release_details["componentId"] = component_id

        url = self.url + "resource/api/releases"
        response = requests.post(
            url, json=release_details, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_release(self, release, release_id):
        """Update an existing release

        API endpoint: PATCH /releases

        :param release: the new release data
        :param release_id: the id of the release to be deleted
        :type release: JSON
        :type release_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id
        response = requests.patch(url, json=release, headers=self.api_headers)
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def update_release_external_id(self, ext_id_name, ext_id_value,
                                   release_id, update_mode="none"):
        """Set or update external id of a release. If the id is already set, it
        will only be changed if `update_mode=="overwrite"`. The id can be
        deleted using `update_mode=="delete"`.

        The method will return the old value of the external id or None if it
        was not set.

        API endpoint: PATCH /releases

        :param ext_id_name: name of the external id
        :param ext_id_value: value of the external id
        :param release_id: the id of the release to be updated
        :param update_mode: can be "none" (default), "overwrite" or "delete"
        :type ext_id_name: string
        :type ext_id_value: string
        :type release_id: string
        :type update_mode: string
        :return: old value of external id
        :rtype: string
        :raises SW360Error: if there is a negative HTTP response
        """
        complete_data = self.get_release(release_id)
        ret = self._update_external_ids(complete_data, ext_id_name,
                                        ext_id_value, update_mode)
        (old_value, data, update) = ret
        if update:
            self.update_release(data, release_id)
        return old_value

    def delete_release(self, release_id):
        """Delete an existing release

        API endpoint: DELETE /releases

        :param release_id: the id of the release to be deleted
        :type release_id: string
        :return: SW360 result
        :rtype: JSON SW360 result object
        :raises SW360Error: if there is a negative HTTP response
        """

        if not release_id:
            raise SW360Error(message="No release id provided!")

        url = self.url + "resource/api/releases/" + release_id
        response = requests.delete(
            url, headers=self.api_headers
        )
        if response.ok:
            return response.json()

        raise SW360Error(response, url)

    def get_users_of_release(self, release_id):
        """Get information of about the users of a release

        API endpoint: GET /releases/usedBy/{id}

        :param release_id: the id of the release to be requested
        :type release_id: string
        :return: all users of this release
        :rtype: JSON objects
        :raises SW360Error: if there is a negative HTTP response
        """

        resp = self.api_get(self.url + "resource/api/releases/usedBy/" + release_id)
        return resp
