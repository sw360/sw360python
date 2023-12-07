# -------------------------------------------------------------------------------
# Copyright (c) 2019-2023 Siemens
# Copyright (c) 2022 BMW CarIT GmbH
# All Rights Reserved.
# Authors: thomas.graf@siemens.com, gernot.hillier@siemens.com
# Authors: helio.chissini-de-castro@bmw.de
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import json
from typing import Any, Dict, Optional

from requests import Response


class SW360Error(IOError):
    """Base exception for SW360 operations

    :param message: a general error message
    :param response: the response object returned by the requests call
    :param url: the URL where the error occurred
    :type message: string
    :type response: object
    :type url: string
    """

    def __init__(self, response: Optional[Response] = None, url: str = "", message: str = ""):
        self.message: str = message
        self.response: Optional[Response] = response
        self.url: str = url
        self.details: Optional[Dict[str, Any]] = None

        try:
            if response is not None:
                self.details = json.loads(response.text)
        except json.JSONDecodeError:
            self.details = None

        if message:
            super().__init__(message)
        else:
            super().__init__(str(response))
