# -------------------------------------------------------------------------------
# Copyright (c) 2020 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
import unittest

sys.path.insert(1, "..")

from sw360 import SW360  # noqa: E402


class Sw360TestSupportMethods(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def test_get_id_from_href(self):
        URL = "https://sw360.siemens.com/resource/api/releases/00dc0db789f9372ed6bcfd55f100e3ce"

        lib = SW360(self.MYURL, self.MYTOKEN, False)
        actual = lib.get_id_from_href(URL)
        self.assertEqual("00dc0db789f9372ed6bcfd55f100e3ce", actual)


if __name__ == "__main__":
    unittest.main()
