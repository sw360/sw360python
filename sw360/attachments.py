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

import json
import logging
import os
from http import HTTPStatus

import requests

from .sw360error import SW360Error

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class AttachmentsMixin:
    def get_attachment_infos_by_hash(self, hashvalue):
        """Get information about attachments with a given sha1 hash value.

        This usually returns zero or one result, but if the same binary file
        was uploaded and attached to multiple sw360 resources, it will return
        all matching attachments for the given hash.

        API endpoint: GET /attachments?sha1=
        """

        resp = self.api_get(
            self.url + "resource/api/attachments?sha1=" + hashvalue
        )
        return resp

    def get_attachment_infos_for_resource(self, resource_type, resource_id):
        """Get information about the attachments of a specific resource.

        Usually, you don't need to call this directly, but use one of the
        specific get_attachment_infos_for_{release,component,project} functions.
        """

        resp = self.api_get(
            self.url + "resource/api/"
            + resource_type
            + "/"
            + resource_id
            + "/attachments"
        )

        if "_embedded" not in resp:
            return None

        if "sw360:attachments" not in resp["_embedded"]:
            return None

        resp = resp["_embedded"]["sw360:attachments"]
        return resp

    def get_attachment_infos_for_release(self, release_id):
        """Get information about the attachments of a release

        :param release_id: id of the release from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("releases", release_id)
        return resp

    def get_attachment_infos_for_component(self, component_id):
        """Get information about the attachments of a component

        :param component_id: id of the component from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("components", component_id)
        return resp

    def get_attachment_infos_for_project(self, project_id):
        """Get information about the attachments of a project

        :param project_id: id of the project from which to list attachments
        """

        resp = self.get_attachment_infos_for_resource("projects", project_id)
        return resp

    def get_attachment_by_url(self, url):
        """Get information about attachment.

        :param url: the full url of the attachment to be requested
        """
        resp = self.api_get(url)
        return resp

    def get_attachment(self, attachment_id):
        """Get information about an attachment

        API endpoint: GET /attachments

        :param attachment_id: id of the attachment
        """

        resp = self.api_get(self.url + "resource/api/attachments/" + attachment_id)
        return resp

    def download_release_attachment(self, filename, release_id, attachment_id):
        """Downloads an attachment of a release

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "releases", release_id, attachment_id
        )

    def download_project_attachment(self, filename, project_id, attachment_id):
        """Downloads an attachment of a project

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "projects", project_id, attachment_id
        )

    def download_component_attachment(self, filename, component_id, attachment_id):
        """Downloads an attachment of a component

        API endpoint: GET /attachments
        """

        self.download_resource_attachment(
            filename, "components", component_id, attachment_id
        )

    def download_resource_attachment(self, filename, resource_type, resource_id, attachment_id):
        """Downloads an attachment from SW360 (only for internal use)

        API endpoint: GET /attachments
        """

        if not resource_id:
            raise SW360Error(message="No resource id provided!")

        if not attachment_id:
            raise SW360Error(message="No attachment id provided!")

        url = (
            self.url
            + "resource/api/"
            + resource_type
            + "/"
            + resource_id
            + "/attachments/"
            + attachment_id
        )
        self.download_attachment(filename, url)

    def download_attachment(self, filename, download_url):
        """Downloads an attachment from SW360

        API endpoint: GET /attachments
        """

        hdr = self.api_headers.copy()
        hdr["Accept"] = "application/*"
        req = requests.get(download_url, allow_redirects=True, headers=hdr)
        if req.ok:
            open(filename, "wb").write(req.content)
        else:
            raise SW360Error(req, download_url)

    def _upload_resource_attachment(self, resource_type, resource_id, upload_file,
                                    upload_type="SOURCE", upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for the resource with the given id
        using `upload_comment` for it. `upload_type` can be
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
        """
        if not os.path.exists(upload_file):
            raise SW360Error(message="ERROR: file not found: " + upload_file)

        if resource_type not in ("releases", "components", "projects"):
            raise SW360Error(message="Invalid resource type provided!")

        if type(resource_id) is not str:
            raise SW360Error(message="Invalid resource id provided!")

        filename = os.path.basename(upload_file)
        url = self.url + "resource/api/" + resource_type + "/" + resource_id + "/attachments"
        attachment_data = {"filename": filename,
                           "attachmentContentId": "2",
                           "createdComment": upload_comment,
                           "attachmentType": upload_type}
        file_data = {
            "file": (filename, open(upload_file, "rb"), "multipart/form-data"),
            "attachment": (
                "",  # dummy filename
                json.dumps(attachment_data),
                "application/json",
            ),
        }
        response = requests.post(url, headers=self.api_headers, files=file_data)
        if response.status_code == HTTPStatus.ACCEPTED:
            logger.warning(
                f"Attachment upload was accepted by {url} but might not be visible yet: {response.text}"
            )
        if not response.ok:
            raise SW360Error(response, url)

    def upload_release_attachment(self, release_id, upload_file, upload_type="SOURCE",
                                  upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `release_id`,
        using `upload_comment` for it. `upload_type` can be
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
        """

        self._upload_resource_attachment(
            "releases", release_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)

    def upload_component_attachment(self, component_id, upload_file, upload_type="SOURCE",
                                    upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `component_id`,
        using `upload_comment` for it. `upload_type` can be
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
        """

        self._upload_resource_attachment(
            "components", component_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)

    def upload_project_attachment(self, project_id, upload_file, upload_type="SOURCE",
                                  upload_comment=""):
        """Upload `upload_file` as attachment to SW360 for `project_id` of,
        using `upload_comment` for it. `upload_type` can be
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
        """

        self._upload_resource_attachment(
            "projects", project_id, upload_file,
            upload_type=upload_type, upload_comment=upload_comment)
