# -------------------------------------------------------------------------------
# (c) 2019-2025 Siemens AG
# All Rights Reserved.
# Author: gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

"""Preview of High-Level, object oriented Python interface to the SW360 REST API.
For now, this does NOT strive to be stable or complete. Feel free to use it as
a more convenient abstraction for some (important) objects, but be prepared for
changes."""

import re
import os
import json
import packageurl


class SW360Resource:
    """Base class representing an SW360 resource like project, component,
    release etc.
    """

    all_resources = {}

    def __new__(cls, json=None, resource_id=None, **kwargs):
        """Check if this resource already exists."""
        key = None
        if resource_id:
            key = (cls.__name__, resource_id)
        elif json and "id" in json:
            key = (cls.__name__, json["id"])

        if key:
            if key not in cls.all_releases:
                cls.all_resources[key] = super(SW360Resource, cls).__new__(cls)
            return cls.all_resources[key]
        else:
            return super(SW360Resource, cls).__new__(cls)

    def __init__(self, json=None, resource_id=None, parent=None, users={}, sw360=None, **kwargs):
        if not hasattr(self, "details"):
            self.details = {}
        """All resource details which are not explicitely supported by the
        constructor parameters of the derived objexts are stored in the
        `details` attribute. Shall use names and types as specified in SW360
        REST API."""

        if not hasattr(self, "users"):
            self.users = {}

        if resource_id and getattr(self, "id", resource_id) != resource_id:
            raise ValueError("Resource id mismatch", self.id, resource_id)
        self.id = resource_id
        """All SW360 resource instances have an `id`. If it is set to `None`,
        the object is yet unknown to SW360 - otherwise, it stores the SW360
        id (release_id, component_id, etc.)."""

        if parent and hasattr(self, "parent"):
            if self.parent.id != parent.id:
                raise ValueError("Resource parent mismatch", self.parent.id, parent.id)
        self.parent = parent

        for k, v in users.items():
            # merge new users with existing ones
            self.users[k] = v

        self.sw360 = sw360
        """SW360 api object"""

        for key, value in kwargs.items():
            self.details[key] = value

        if json is not None:
            self.from_json(json)

    def __setattr__(self, name, value):
        # assure that the resource is registered in the global resource list
        # even if the id is set later
        super().__setattr__(name, value)
        if name == "id" and value is not None:
            key = (self.__class__.__name__, value)
            self.all_resources[key] = self

    def _parse_release_list(self, json_list, parent=None, users={}):
        """Parse a JSON list of releases, create according objects and add
        them to `container`."""
        releases = {}
        for release_json in json_list:
            release = Release(parent=parent, users=users, sw360=self.sw360)
            release.from_json(release_json)
            releases[release.id] = release
        return releases

    def _parse_attachment_list(self, json_list, parent=None):
        """Parse a JSON list of releases, create according objects and add
        them to `container`."""
        attachments = {}
        for attachment_json in json_list:
            attachment = Attachment(parent=parent, sw360=self.sw360)
            attachment.from_json(attachment_json)
            attachments[attachment.id] = attachment
        return attachments

    def _parse_project_list(self, json_list, users={}):
        """Parse a JSON list of projects, create according objects and add
        them to `container`."""
        projects = {}
        for project_json in json_list:
            project = Project(users=users, sw360=self.sw360)
            project.from_json(project_json)
            projects[project.id] = project
        return projects

    def _parse_link(self, key, links_key, links_value):
        """Parse a _links or _embedded section in JSON"""
        if links_key == "sw360:component":
            self.parent = Component(component_id=links_value["href"].split("/")[-1], sw360=self.sw360)
        elif links_key == "sw360:downloadLink":
            self.download_link = links_value["href"]
        elif links_key == "sw360:attachments":
            self.attachments = self._parse_attachment_list(
                links_value,
                parent=self)
        elif links_key == "sw360:releases":
            if isinstance(self, Component):
                parent = self
                users = {}
            else:
                parent = None
                users = {self.id: self}
            self.releases = self._parse_release_list(
                links_value, parent=parent, users=users)
        elif links_key == "sw360:projects":
            self.projects = self._parse_project_list(
                links_value, {self.id: self})
        elif links_key == "self":
            self.id = links_value["href"].split("/")[-1]
        else:
            self.details.setdefault(key, {})
            self.details[key][links_key] = links_value

    def _parse_purls(self, purl_value):
        """Parse package url strings"""
        purls = []
        if type(purl_value) is str:
            if purl_value.startswith("["):
                # as of 2022-04, SW360 returns arrays as JSON string...
                purl_value = json.loads(purl_value)
            else:
                purl_value = purl_value.split()

        for purl_string in purl_value:
            if purl_string.startswith("pkg:"):
                try:
                    purl = packageurl.PackageURL.from_string(purl_string)
                    purls.append(purl)
                except ValueError:
                    pass
        return purls

    _camel_case_pattern = re.compile(r'(?<!^)(?=[A-Z])')

    def from_json(self, json, copy_attributes=list(), snake_case=True):
        """`copy_attributes` will be copied as-is between this instance's
        attributes and JSON members. If `snake_case` is set, more Python-ish
        snake_case names will be used (project_type instead of projectType).
        """
        # delete purl list as we add purls from different external ids below
        self.purls = []
        for key, value in json.items():
            if key in copy_attributes:
                if snake_case:
                    key = self._camel_case_pattern.sub('_', key).lower()
                if key == "external_ids":
                    for id_type, id_value in value.items():
                        # detect purls independent from id_type - it should be
                        # 'package-url', but some use "purl", "purl.id", etc.
                        purls = self._parse_purls(id_value)
                        if len(purls):
                            self.purls += purls
                            continue
                        self.external_ids[id_type] = id_value
                else:
                    self.__setattr__(key, value)
            elif key in ("_links", "_embedded"):
                for links_key, links_value in value.items():
                    self._parse_link(key, links_key, links_value)
            else:
                self.details[key] = value

    def __repr__(self):
        repr_ = []
        for k, v in self.__dict__.items():
            if v is None:
                continue
            if (k in ("name", "version", "filename", "attachment_type")
                    or k.endswith("_id")):
                repr_.append(f'{k}={v!r}')
            if k == "id":
                repr_.append(f'{self.__class__.__name__.lower()}_id={v!r}')
        return (f'{self.__class__.__name__}('
                + ", ".join(repr_)
                + ")")


class Release(SW360Resource):
    """A release is the SW360 abstraction for a single version of a component.

    You can either create it from a SW360 `json` object or by specifying the
    details via the constructor parameters, see list below. Only the most
    important attributes are supported, rest hast be provided via `kwargs` and
    is stored in the `details` attribute of instances.

    For JSON parsing, please read documentation of from_json() method.

    :param json: create release from SW360 JSON object by calling from_json()
    :param parent: SW360 component the release belongs to
    :param users: dictionary of SW360 resources which link to the release
                  (instances of Release() or Project() with id as key)
    :param version: the actual version
    :param downloadurl: URL the release was downloaded from
    :param release_id: id of the release (if exists in SW360 already)
    :param sw360: your SW360 instance for interacting with the API
    :param kwargs: additional relase details as specified in the SW360 REST API
    :type json: SW360 JSON object
    :type parent: Component() object
    :type users: dictionary
    :type version: string
    :type downloadurl: string
    :type release_id: string
    :type sw360: instance from SW360 class
    :type kwargs: dictionary
    """
    def __init__(self, json=None, release_id=None, parent=None, users={},
                 name=None, version=None, downloadurl=None, sw360=None, **kwargs):
        self.attachments = {}
        self.external_ids = {}
        self.purls = []

        self.name = name
        self.version = version
        self.downloadurl = downloadurl
        super().__init__(json=json, resource_id=release_id, parent=parent, users=users,
                         sw360=sw360, **kwargs)

    def from_json(self, json):
        """Parse release JSON object from SW360 REST API. The component it
        belongs to will be extracted and stored in the `parent`
        attribute.

        SW360 external ids will be stored in the `external_ids` attribute.
        If valid package URLs (https://github.com/package-url/purl-spec) are found
        in the external ids, they will be stored in the `purls` attribute as
        packageurl.PackageURL instances.

        All details not directly supported by this class will be stored as-is
        in the `details` instance attribute. Please note that this might
        change in future if more abstractions will be added here."""
        super().from_json(
            json,
            copy_attributes=("name", "version", "downloadurl", "externalIds"))

    def get(self, sw360=None, id_=None):
        """Retrieve/update release from SW360."""
        if sw360:
            self.sw360 = sw360
        if id_:
            self.id = id_
        self.from_json(self.sw360.get_release(self.id))
        return self

    def __str__(self):
        return f'{self.name} {self.version} ({self.id})'


class Attachment(SW360Resource):
    """An attachment is used to store all kinds of files in SW360, for example
    upstream source files (attachment_type "SOURCE"), self-created source file bundles
    ("SOURCE_SELF"), clearing reports ("CLEARING_REPORT") or CLI files
    ("COMPONENT_LICENSE_INFO_XML").

    You can either create it from a SW360 `json` object or by specifying the
    details via the constructor parameters, see list below. Only the most
    important attributes are supported, rest hast be provided via `kwargs` and
    is stored in the `details` attribute of instances.

    For JSON parsing, please read documentation of from_json() method.

    :param json: create it from SW360 JSON object by calling from_json()
    :param attachment_id: SW360 id of the attachment (if it exists already)
    :param parent: SW360 resource (release, component or project) the attachment belongs to
    :param filename: the filename of the attachment
    :param sha1: SHA1 sum of the file to check its integrity
    :param attachment_type: one of "DOCUMENT", "SOURCE", "SOURCE_SELF"
           "CLEARING_REPORT", "COMPONENT_LICENSE_INFO_XML", "BINARY",
           "BINARY_SELF", "LICENSE_AGREEMENT", "README_OSS"
    :param sw360: your SW360 instance for interacting with the API
    :param kwargs: additional relase details as specified in the SW360 REST API
    :type json: SW360 JSON object
    :type attachment_id: string
    :type release_id: string
    :type filename: string
    :type sha1: string
    :type attachment_type: string
    :type sw360: instance from SW360 class
    :type kwargs: dictionary
    """
    def __init__(self, json=None, attachment_id=None, parent=None,
                 filename=None, sha1=None, attachment_type=None, sw360=None, **kwargs):
        self.attachment_type = attachment_type
        self.filename = filename
        self.sha1 = sha1
        self.download_link = None
        super().__init__(json=json, resource_id=attachment_id, parent=parent,
                         sw360=sw360, **kwargs)

    def from_json(self, json):
        """Parse attachment JSON object from SW360 REST API. For now, we don't
        support parsing the resource the attachment belongs to, so this needs
        to be set via constructur.

        SW360 external ids will be stored in the `external_ids` attribute.
        If valid package URLs (https://github.com/package-url/purl-spec) are found
        in the external ids, they will be stored in the `purls` attribute as
        packageurl.PackageURL instances.

        All details not directly supported by this class will be stored as-is
        in the `details` instance attribute.
        Please note that this might change in future if more abstractions
        will be added in this Python library."""
        super().from_json(
            json,
            copy_attributes=("filename", "sha1", "attachmentType",
                             "createdBy", "createdTeam", "createdComment", "createdOn",
                             "checkedBy", "checkedTeam", "checkedComment", "checkedOn",
                             "checkStatus"))

    def get(self, sw360=None, id_=None):
        """Retrieve/update attachment from SW360."""
        if sw360:
            self.sw360 = sw360
        if id_:
            self.id = id_
        self.from_json(self.sw360.get_attachment(self.id))
        return self

    def download(self, target_path, filename=None):
        """download an attachment to local file.

        :param target_path: path where to store the attachment
        :type target_path: str
        :param filename: local filename. If not given, use the filename stored in SW360
        :type filename: str, optional
        """
        if filename is None:
            filename = os.path.basename(self.filename)
        self.sw360.download_attachment(os.path.join(target_path, filename),
                                       self.download_link)

    def __str__(self):
        return f'{self.filename} ({self.id})'


class Component(SW360Resource):
    """A component is the SW360 abstraction for a single software
    package/library/program/etc.

    You can either create it from a SW360 `json` object or by specifying the
    details via the constructor parameters, see list below. Only the most
    important attributes are supported, rest hast be provided via `kwargs` and
    is stored in the `details` attribute of instances.

    For JSON parsing, please read documentation of from_json() method.

    :param json: create component from SW360 JSON object by calling from_json()
    :param component_id: id of the component (if exists in SW360 already)
    :param name: name of the component
    :param description: short description for component
    :param homepage: homepage of the component
    :param component_type: one of "INTERNAL", "OSS", "COTS", "FREESOFTWARE",
                           "INNER_SOURCE", "SERVICE", "CODE_SNIPPET"
    :param sw360: your SW360 instance for interacting with the API
    :param kwargs: additional component details as specified in the SW360 REST API
    :type json: SW360 JSON object
    :type component_id: string
    :type name: string
    :type description: string
    :type homepage: string
    :type component_type: string
    :type sw360: instance from SW360 class
    :type kwargs: dictionary
    """
    def __init__(self, json=None, component_id=None, name=None, description=None,
                 homepage=None, component_type=None, sw360=None, **kwargs):
        self.releases = {}
        self.attachments = {}
        self.external_ids = {}
        self.purls = []

        self.name = name
        self.description = description
        self.homepage = homepage
        self.component_type = component_type

        super().__init__(json=json, resource_id=component_id, sw360=sw360, **kwargs)

    def from_json(self, json):
        """Parse component JSON object from SW360 REST API. Information for
        its releases will be extracted, Release() objects created for them
        and stored in the `releases` instance attribue. Please note that
        the REST API will only provide basic information for the releases.

        SW360 external ids will be stored in the `external_ids` attribute.
        If valid package URLs (https://github.com/package-url/purl-spec) are found
        in the external ids, they will be stored in the `purls` attribute as
        packageurl.PackageURL instances.

        All details not directly supported by this class will be
        stored as-is in the `details` instance attribute. For now, this also
        includes vendor information which will be stored as-is in
        `details['_embedded']['sw360:vendors']`. Please note that this might
        change in future if more abstractions will be added here."""
        super().from_json(
            json,
            copy_attributes=("name", "description", "homepage",
                             "componentType", "externalIds"))

    def get(self, sw360=None, id_=None):
        """Retrieve/update component from SW360."""
        if sw360:
            self.sw360 = sw360
        if id_:
            self.id = id_
        self.from_json(self.sw360.get_component(self.id))
        return self

    def __str__(self):
        return f'{self.name} ({self.id})'


class Project(SW360Resource):
    """A project is SW360 abstraction for a collection of software releases
    used in a project/product. It can contain links to other `Project`s or
    `Release`s.

    You can either create it from a SW360 `json` object or by specifying the
    details via the constructor parameters, see list below. Only the most
    important attributes are supported, rest hast be provided via `kwargs` and
    is stored in the `details` attribute of instances.

    For JSON parsing, please read documentation of from_json() method.

    :param json: create component from SW360 JSON object by calling from_json()
    :param project_id: id of the project (if exists in SW360 already)
    :param users: dictionary of SW360 resources which link to the project
                  (instances of Project() with id as key)
    :param name: name of the project
    :param version: version of the project
    :param description: short description for project
    :param visibility: project visibility in SW360, one of "PRIVATE",
                       "ME_AND_MODERATORS", "BUISNESSUNIT_AND_MODERATORS",
                       "EVERYONE"
    :param project_type: one of "CUSTOMER", "INTERNAL", "PRODUCT", "SERVICE",
                         "INNER_SOURCE"
    :param sw360: your SW360 instance for interacting with the API
    :param kwargs: additional project details as specified in the SW360 REST API
    :type json: SW360 JSON object
    :type project_id: string
    :type name: string
    :type version: string
    :type description: string
    :type visibility: string
    :type project_type: string
    :type sw360: instance from SW360 class
    :type kwargs: dictionary
    """
    def __init__(self, json=None, project_id=None, users={},
                 name=None, version=None, description=None, visibility=None, project_type=None,
                 sw360=None, **kwargs):
        self.releases = {}
        self.external_ids = {}
        self.purls = []

        self.name = name
        self.version = version
        self.description = description
        self.visibility = visibility
        self.project_type = project_type
        super().__init__(json=json, resource_id=project_id, users=users,
                         sw360=sw360, **kwargs)

    def from_json(self, json):
        """Parse project JSON object from SW360 REST API. Information for
        its releases will be extracted, Release() objects created for them
        and stored in the `releases` instance attribue. Please note that
        the REST API will only provide basic information for the releases.

        SW360 external ids will be stored in the `external_ids` attribute.
        If valid package URLs (https://github.com/package-url/purl-spec) are found
        in the external ids, they will be stored in the `purls` attribute as
        packageurl.PackageURL instances.

        All details not directly supported by this class will be
        stored as-is in the `details` instance attribute. For now, this also
        includes linked projects. Please note that this might change in future
        if better abstractions will be added here."""
        super().from_json(
            json,
            copy_attributes=("name", "description", "version", "visibility",
                             "projectType", "externalIds"))

    def get(self, sw360=None, id_=None):
        """Retrieve/update project from SW360."""
        if sw360:
            self.sw360 = sw360
        if id_:
            self.id = id_
        self.from_json(self.sw360.get_project(self.id))
        return self

    def __str__(self):
        return f'{self.name} {self.version} ({self.id})'
