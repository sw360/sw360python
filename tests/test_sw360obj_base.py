# -------------------------------------------------------------------------------
# Copyright (c) 2020-2025 Siemens
# All Rights Reserved.
# Author: gernot.hillier@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import unittest
import responses
from sw360 import SW360


SW360_BASE_URL = "https://sw360.siemens.com/resource/api/"


class Sw360ObjTestBase(unittest.TestCase):
    @responses.activate
    def setUp(self):
        responses.add(
            responses.GET,
            SW360_BASE_URL,
            json={"status": "ok"})
        self.lib = SW360("https://sw360.siemens.com", "mytoken")
        self.lib.login_api()
