# -------------------------------------------------------------------------------
# Copyright (c) 2023-2026 Siemens
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, mishra.gaurav@siemens.com
# Authors: gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import json
import logging
import os
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode

import requests

from .sorting import SortParam
from .sw360error import SW360Error

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class SW360Response(Dict[str, Any]):
    """A regular dict response with convenience methods for HAL traversal.

    Behaves identically to a plain ``dict`` for backward compatibility, but
    adds ``linked_id()``, ``linked_ids()``, ``embedded_list()``, and
    ``embedded_lists()`` for comfortable access to ``_links`` and
    ``_embedded`` sections.
    """

    def linked_id(self, link_key: str = "self") -> Optional[str]:
        """Extract a resource ID from a ``_links`` entry.

        Convenience shortcut for ``BaseMixin.get_linked_id(self, link_key)``.

        :param link_key: the link relation key, defaults to ``"self"``
        :return: the resource ID, or ``None`` if not available
        """
        return BaseMixin.get_linked_id(self, link_key)

    def linked_ids(self) -> Dict[str, str]:
        """Return all linked resource IDs as a dict.

        Iterates all entries in ``_links`` and resolves each href to its
        resource ID, returning a mapping of link key to ID. Useful for
        inspecting which linked resources are available.

        :return: dict mapping each link key to its resource ID
        """
        links = self.get("_links")
        if not isinstance(links, dict):
            return {}
        return {
            key: BaseMixin.get_id_from_href(entry["href"])
            for key, entry in links.items()
            if isinstance(entry, dict) and isinstance(entry.get("href"), str)
        }

    def embedded_list(self, key: str) -> List["SW360Response"]:
        """Retrieve a specific embedded resource list.

        Like ``BaseMixin.get_embedded()``, but each item in the returned
        list is wrapped in ``SW360Response`` so that ``.linked_id()`` and
        other convenience methods are available on the items.

        :param key: the embedded resource key, e.g. ``"releases"``
        :return: list of embedded resources as ``SW360Response`` objects,
            or ``[]`` if not present
        """
        return [SW360Response(item) for item in BaseMixin.get_embedded(self, key)]

    def embedded_lists(self) -> Dict[str, List["SW360Response"]]:
        """Return all embedded resource lists as a dict.

        Iterates all entries in ``_embedded`` and wraps each item in
        ``SW360Response``. Useful for inspecting which embedded resources
        are available.

        :return: dict mapping each embedded key to its list of
            ``SW360Response`` objects
        """
        embedded = self.get("_embedded")
        if not isinstance(embedded, dict):
            return {}
        return {
            key: [SW360Response(item) for item in items]
            for key, items in embedded.items()
            if isinstance(items, list)
        }


class BaseMixin():
    """Python interface to the Siemens SW360 platform

    Authentication against a running SW360 instance is performed using an API token.
    The token will be sent as HTTP header using the format
    `Authorization: <token_type> <token>`. Check your SW360 REST API
    documentation for details on needed type and how to get the token.
    token_type is "Bearer" for an OAuth workflow and "Token" for tokens
    generated via the SW360 UI.

    :ivar url: URL of the SW360 instance
    :ivar token: The SW360 REST API token (the cryptic string without
     "Authorization:" and `token_type`).
    :ivar oauth2: flag indicating whether this is an OAuth2 token
    :ivar default_batch_size: Default size of batch to use while fetching all items from API
    :type url: string
    :type token: string
    :type oauth2: boolean
    :type default_batch_size: int
    """

    def __init__(self, url: str, token: str, oauth2: bool = False,
                 default_batch_size: int = 50) -> None:
        """Constructor"""
        if url[-1] != "/":
            url += "/"
        self.url = url
        self.session: Optional[requests.Session] = None

        if oauth2:
            self.api_headers = {"Authorization": "Bearer " + token}
        else:
            self.api_headers = {"Authorization": "Token " + token}

        self.force_no_session = False
        self.default_batch_size = default_batch_size
        self.api_version = (18, 0)

    def api_get(self, url: str = "") -> Optional[SW360Response]:
        """Request `url` from REST API and return json answer.

        :param url: the url to be requested
        :type url: string
        :return: JSON data as dict with convenience methods for HAL traversal
        :rtype: SW360Response
        :raises SW360Error: if there is a negative HTTP response
        """

        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.get(url, headers=self.api_headers)
        else:
            if self.session:
                response = self.session.get(url)

        if response.ok:
            if response.status_code == HTTPStatus.NO_CONTENT:
                return None
            parsed = response.json()
            if isinstance(parsed, dict):
                return SW360Response(parsed)
            else:
                return parsed

        raise SW360Error(response, url)

    def api_get_all(self, url: str, sort: Optional[SortParam] = None,
                    batch: int = -1, page: int = 0,
                    _data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve all pages of data from the specified URL.

        :param url: The URL to request data from.
        :param sort: The sort parameter to sort data by.
        :param page: Page number to fetch
        :param batch: How many rows to fetch at a time, use
                      `default_batch_size` if -1
        :param _data: Internal param for aggregating data.
        :return: The combined JSON data from all pages.
        :rtype: Optional[Dict[str, Any]]
        """
        if _data is None:
            _data = {}
        if batch == -1:
            batch = self.default_batch_size

        paginated_url = self._add_pagination(url, page, batch, sort)
        resp = self.api_get(paginated_url)
        if resp is not None and 'page' in resp:
            total_pages = resp['page']['totalPages']
            # Clean up meta info
            if '_links' in resp:
                del resp['_links']
            del resp['page']
            # Update data and get next page
            _data = self.__merge_responses(_data, resp)
            if page + 1 < total_pages:
                return self.api_get_all(url, sort, batch, page + 1, _data)
        else:
            # Clean up meta info
            if resp is not None and '_links' in resp:
                del resp['_links']
            _data = self.__merge_responses(_data, resp)
        return _data

    def __merge_responses(self, previous: Dict[str, Any],
                          next: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Function to merge previous and next response of the same API
        recursively.
        :param previous: The previous response data.
        :param next: The next response data.
        :return: The merged response data.
        """
        if next is None:
            return previous
        for key, value in next.items():
            if (key in previous and isinstance(previous[key], dict) and
                    isinstance(value, dict)):
                previous[key] = self.__merge_responses(previous[key], value)
            elif (key in previous and isinstance(previous[key], list) and
                    isinstance(value, list)):
                previous[key].extend(value)
            elif (key in previous and isinstance(previous[key], tuple) and
                    isinstance(value, tuple)):
                previous[key].extend(value)
            else:
                previous[key] = value
        return previous

    def api_post_multipart(self, url: str = "", files: Dict[str, Any] = {}) -> Optional[requests.Response]:
        """
        Send a multipart POST request to the specified URL with the provided file data.

        :param url: The URL to send the multipart POST request to.
        :type url: str
        :param files: The dictionary containing file data to be sent in the request.
        :type files: Dict[str, Any]
        :return: The JSON response received from the server, if any.
        :rtype: Optional[Dict[str, Any]]
        :raises SW360Error: If the HTTP response indicates an error.
        """

        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.post(url, headers=self.api_headers, files=files)
        else:
            if self.session:
                response = self.session.post(url, files=files)

        if response.ok:
            if response.status_code == HTTPStatus.NO_CONTENT:  # 204 No Content
                return None
            return response

        raise SW360Error(response, url)

    def api_post(
        self,
        url: str = "",
        json: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    ) -> Optional[requests.Response]:

        """
        Send a POST request to the specified URL with the provided json data.

        :param url: The URL to send the POST request to.
        :type url: str
        :param json: The dictionary containing json data to be sent in the request.
        :type json: Dict[str, Any]
        :return: The JSON response received from the server, if any.
        :rtype: Optional[Dict[str, Any]]
        :raises SW360Error: If the HTTP response indicates an error.
        """

        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.post(url, headers=self.api_headers, json=json)
        else:
            if self.session:
                response = self.session.post(url, json=json)

        if response.ok:
            if response.status_code == HTTPStatus.NO_CONTENT:  # 204 No Content
                return None
            return response

        raise SW360Error(response, url)

    def api_patch(self, url: str = "", json: Any = {}) -> Optional[SW360Response]:
        """
        Send a PATCH request to the specified URL with the provided json data.

        :param url: The URL to send the PATCH request to.
        :type url: str
        :param json: The dictionary containing json data to be sent in the request.
        :type json: Dict[str, Any]
        :return: The JSON response as dict with convenience methods for HAL traversal
        :rtype: Optional[SW360Response]
        :raises SW360Error: If the HTTP response indicates an error.
        """
        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.patch(url, headers=self.api_headers, json=json)
        else:
            if self.session:
                response = self.session.patch(url, json=json)

        if response.ok:
            if response.status_code == HTTPStatus.NO_CONTENT:  # 204 No Content
                return None
            if response.content:
                parsed = response.json()
                if isinstance(parsed, dict):
                    return SW360Response(parsed)
                else:
                    return parsed
            else:
                return None

        raise SW360Error(response, url)

    def api_delete(self, url: str = "") -> Optional[requests.Response]:
        """Send a DELETE request to the specified `url` of the REST API and return JSON response.

        :param url: The URL to which the DELETE request will be sent.
        :type url: str
        :return: JSON data returned by the API, or None if the response is empty.
        :rtype: Optional[Dict[str, Any]]
        :raises SW360Error: If the API responds with a non-success HTTP status code.
        """
        if (not self.force_no_session) and self.session is None:
            raise SW360Error(message="login_api needs to be called first")

        if self.force_no_session:
            response = requests.delete(url, headers=self.api_headers)
        else:
            if self.session:
                response = self.session.delete(url)

        if response.ok:
            if response.status_code == HTTPStatus.NO_CONTENT:
                return None
            return response

        raise SW360Error(response, url)

    def _update_external_ids(self, current_data: Dict[str, Any], ext_id_name: str, ext_id_value: str,
                             update_mode: str) -> Tuple[Optional[Any], Dict[str, Dict[str, str]], bool]:
        """Internal helper function to prepare an update/addition of external
        id while preserving the others."""
        old_value = None
        if "externalIds" not in current_data:
            ext_id_data = {"externalIds": {ext_id_name: ext_id_value}}
        else:
            if ext_id_name in current_data["externalIds"]:
                old_value = current_data["externalIds"][ext_id_name]
            ext_id_data = {"externalIds": current_data["externalIds"]}
            ext_id_data["externalIds"][ext_id_name] = ext_id_value

        if update_mode == "delete":
            del ext_id_data["externalIds"][ext_id_name]

        if (update_mode == "overwrite"
                or (update_mode == "none" and old_value is None)
                or (update_mode == "delete" and old_value is not None)):
            update = True
        else:
            update = False

        return (old_value, ext_id_data, update)

    @staticmethod
    def _add_params(url: str, params: Dict[str, str]) -> str:
        """Add the given parameter to the given url"""

        query_string = urlencode(params)

        if query_string == "":
            return url

        if "?" in url:
            return f"{url}&{query_string}"
        else:
            return f"{url}?{query_string}"

    def _add_pagination(self, url: str, page: int, page_entries: int,
                        sort: Optional[SortParam] = None) -> str:
        """
        Add pagination parameters to the GET request URL
        :param url: URL to add params to
        :param page: Page number to fetch
        :param page_entries: Number of entries to fetch per request
        :param sort: Sorting parameter (optional)
        :return: URL with pagination parameters added
        """

        params = {
            "page": str(page),
            "page_entries": str(page_entries)
        }
        if sort is not None:
            params["sort"] = str(sort)

        return self._add_params(url, params)

    @classmethod
    def get_id_from_href(cls, href: str) -> str:
        """Extracts the identifier from the href and returns it

        :param href: HAL href for a specific resource
        :type href: string (valid URL)
        :return: the id part of the href
        :rtype: string
        """

        pos = href.rfind("/")
        identifier = href[(pos + 1):]
        return identifier

    def _upload_resource_file(self, upload_file: str,
                              upload_type: str = "SOURCE",
                              upload_comment: str = "") -> Dict[str, str]:
        """Upload `upload_file` as attachment to SW360 which can then be used
        by various resources as attachment content.
        `upload_type` can be:
        "DOCUMENT"
        "SOURCE"
        "CLEARING_REPORT"
        "COMPONENT_LICENSE_INFO_XML"
        "SOURCE_SELF"
        "BINARY"
        "BINARY_SELF"
        "LICENSE_AGREEMENT"
        "README_OSS"

        API endpoint: POST /attachments

        :return: Returns the attachment content of the uploaded file which
                 can be used by other resources.
        :raises SW360Error: if unable to extract content from the upload
        """
        if not os.path.exists(upload_file):
            raise SW360Error(message="ERROR: file not found: " + upload_file)

        filename = os.path.basename(upload_file)
        url = self.url + "resource/api/attachments"
        attachment_data = {
            "filename": filename,
            "createdComment": upload_comment,
            "attachmentType": upload_type
        }

        file_data = {
            "files": (filename, open(upload_file, "rb"), "multipart/form-data"),
            "attachment": (
                "",  # dummy filename
                json.dumps(attachment_data),
                "application/json",
            ),
        }
        response = self.api_post_multipart(url, files=file_data)
        attachment_content = None
        if response is not None:
            if response.status_code == HTTPStatus.ACCEPTED:
                logger.warning(
                    f"Attachment upload was accepted by {url} but might not be visible yet: {response.text}"
                )
            if response.status_code == HTTPStatus.OK:
                r = response.json()
                if '_embedded' in r and 'sw360:attachments' in r['_embedded'] \
                        and len(r['_embedded']['sw360:attachments']) == 1:
                    content = r['_embedded']['sw360:attachments'][0]
                    attachment_content = {
                        'attachmentContentId': content['attachmentContentId'],
                        'filename': content['filename'],
                        'sha1': content['sha1'],
                        'attachmentType': content['attachmentType'],
                        'createdComment': content['createdComment'],
                        'checkStatus': content['checkStatus']
                    }
            if not response.ok:
                raise SW360Error(response, url)
        if attachment_content is None:
            raise SW360Error(response, url,
                             "Unable to fetch attachment content from the response.")
        return attachment_content

    @staticmethod
    def _get_attachments(
        resource: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        attachments: List[Dict[str, Any]] = []
        if resource is None:
            return attachments
        if 'attachments' in resource:
            attachments.extend(resource['attachments'])
        if '_embedded' in resource and \
                'sw360:attachments' in resource['_embedded']:
            attachments.extend(resource['_embedded']['sw360:attachments'])
        # Remove meta properties like "_links" from attachments
        for attachment in attachments:
            if '_links' in attachment:
                del attachment['_links']
        return attachments

    def is_above_version_18(self) -> bool:
        """Check if API version is above version 18.
         Used to check version >= 19 features."""
        return self.api_version >= (19, 0)

    def is_above_version_19(self) -> bool:
        """Check if API version is above version 19.
         Used to check version >= 20 features."""
        return self.api_version >= (20, 0)

    @classmethod
    def get_linked_id(cls, data: Dict[str, Any], link_key: str = "self") -> Optional[str]:
        """Extract the resource ID from a HAL ``_links`` entry.

        Looks up ``data["_links"][link_key]["href"]`` and returns the last
        path segment, which is the resource identifier in the SW360 REST API.

        It defaults to the "self" link, but can be used for any link relation key
        like "sw360:component" or "sw360:project". The "sw360:" prefix can be
        omitted in the `link_key` argument.

        :param data: a JSON response dict containing a ``_links`` section
        :param link_key: the link relation key, e.g. ``"self"`` or
            ``"sw360:component"``
        :return: the extracted resource ID, or ``None`` if the path does not
            exist
        :rtype: Optional[str]
        """
        links = data.get("_links")
        if not isinstance(links, dict):
            return None

        if link_key in links:
            entry = links.get(link_key)
        else:
            entry = links.get("sw360:" + link_key)
        if not isinstance(entry, dict):
            return None

        href = entry.get("href")
        if not isinstance(href, str):
            return None

        return cls.get_id_from_href(href)

    @classmethod
    def get_embedded(cls, data: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
        """Safely retrieve an embedded resource list from a HAL response.

        Returns ``data["_embedded"][key]`` if it exists and is a list,
        otherwise returns an empty list. The "sw360:" prefix can be omitted
        in the `key` argument.

        :param data: a JSON response dict potentially containing an
            ``_embedded`` section
        :param key: the embedded resource key, e.g. ``"sw360:releases"``
        :return: the list of embedded resources, or ``[]`` if not present
        :rtype: List[Dict[str, Any]]
        """
        embedded = data.get("_embedded")
        if not isinstance(embedded, dict):
            return []

        if key in embedded:
            items = embedded.get(key)
        else:
            items = embedded.get("sw360:" + key)
        if not isinstance(items, list):
            return []

        return items
