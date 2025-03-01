# -------------------------------------------------------------------------------
# Copyright (c) 2019-2025 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

__version__ = (1, 9, 0)

from .sw360_api import SW360
from .sw360error import SW360Error
from .sw360oauth2 import SW360OAuth2
from .sw360_objects import Component, Release, Attachment, Project

__all__ = [
    "SW360",
    "SW360Error",
    "SW360OAuth2",
    "Component",
    "Release",
    "Attachment",
    "Project"
]
