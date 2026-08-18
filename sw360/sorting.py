# ------------------------------------------------------------------------------
# Copyright (c) 2026 Siemens
# All Rights Reserved.
# Authors: mishra.gaurav@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# ------------------------------------------------------------------------------
from enum import Enum


class SortParam:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value


class BaseSortMixin(Enum):
    def asc(self) -> SortParam:
        return SortParam(f"{self.value},asc")

    def desc(self) -> SortParam:
        return SortParam(f"{self.value},desc")


class ProjectSortColumn(BaseSortMixin, Enum):
    SCORE = "score"
    CREATED_ON = "createdOn"
    NAME = "name"
    VENDOR = "vendor"
    LICENSE = "license"
    TYPE = "type"
    DESCRIPTION = "description"
    PROJECT_RESPONSIBLE = "projectResponsible"
    STATE = "state"


class ReleaseSortColumn(BaseSortMixin, Enum):
    CREATED_ON = "createdOn"
    NAME = "name"
    VERSION = "version"
    CLEARING_STATE = "clearingState"
    MAINLINE_STATE = "mainlineState"
    SCORE = "score"


class ComponentSortColumn(BaseSortMixin, Enum):
    SCORE = "score"
    CREATED_ON = "createdOn"
    NAME = "name"
    VENDOR_NAMES = "vendorNames"
    MAIN_LICENSE_IDS = "mainLicenseIds"
    TYPE = "type"


class LicenseSortColumn(BaseSortMixin, Enum):
    SCORE = "score"
    FULL_NAME = "fullName"
    SHORT_NAME = "shortName"


class ModerationSortColumn(BaseSortMixin, Enum):
    SCORE = "score"
    DOCUMENT_NAME = "documentName"
    DOCUMENT_TYPE = "documentType"
    COMPONENT_TYPE = "componentType"
    MODERATION_STATE = "moderationState"
    REQUEST_DATE = "requestDate"
    REQUESTING_USER = "requestingUser"
    REQUESTING_USER_DEPARTMENT = "requestingUserDepartment"
