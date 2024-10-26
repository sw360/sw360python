# -------------------------------------------------------------------------------
# Copyright (c) 2024 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

import sys
import unittest
import warnings

import responses

from sw360 import SW360

sys.path.insert(1, "..")


class Sw360TestModerationRequests(unittest.TestCase):
    MYTOKEN = "MYTOKEN"
    MYURL = "https://my.server.com/"
    ERROR_MSG_NO_LOGIN = "Unable to login"

    def setUp(self) -> None:
        warnings.filterwarnings(
            "ignore", category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

    def _add_login_response(self) -> None:
        """
        Add the response for a successful login.
        """
        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/",
            body="{'status': 'ok'}",
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

    @responses.activate
    def test_get_all_moderation_requests(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/moderationrequest?page=2&page_entries=8&sort=timestamp%2Cdesc",
            body='''{
                "_embedded": {
                    "sw360:moderationRequests": [
                    {
                        "id": "b41ddfb69b40439cabb18538313a036c",
                        "timestamp": 1729870771747,
                        "timestampOfDecision": 0,
                        "documentId": "8d101909d2f24ea592e666e9e9bb9eb0",
                        "documentType": "RELEASE",
                        "requestingUser": "gernot.hillier@siemens.com",
                        "moderators": ["admin2@sw360.org", "thomas.graf@siemens.com"],
                        "documentName": "@grpc/grpc-js (1.9.15)",
                        "moderationState": "PENDING",
                        "requestingUserDepartment": "SI",
                        "componentType": "OSS",
                        "moderatorsSize": 157,
                        "_links": {
                            "self": {
                            "href": "https://my.server.com/resource/api/moderationrequest/b4"
                            }
                        }
                    }]
                },
                "_links": {
                    "first": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=0&page_entries=20"
                    },
                    "next": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=1&page_entries=20"
                    },
                    "last": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=2769&page_entries=20"
                    },
                    "curies": [
                    {
                        "href": "https://my.server.com/resource/docs/{rel}.html",
                        "name": "sw360",
                        "templated": true
                    }
                    ]
                },
                "page": {
                    "size": 20,
                    "totalElements": 5555,
                    "totalPages": 3333,
                    "number": 0
                }
            }''',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        mrs = lib.get_all_moderation_requests(page=2, page_size=8, sort="timestamp,desc")
        self.assertIsNotNone(mrs)
        self.assertTrue(len(mrs) > 0)
        mr_list = mrs["_embedded"]["sw360:moderationRequests"]
        self.assertEqual("@grpc/grpc-js (1.9.15)", mr_list[0]["documentName"])

    @responses.activate
    def test_get_moderation_requests_by_state(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/moderationrequest/byState?state=open&allDetails=true&page=2&page_entries=8&sort=timestamp%2Cdesc",  # noqa
            body='''{
                "_embedded": {
                    "sw360:moderationRequests": [
                    {
                        "id": "b41ddfb69b40439cabb18538313a036c",
                        "timestamp": 1729870771747,
                        "timestampOfDecision": 0,
                        "documentId": "8d101909d2f24ea592e666e9e9bb9eb0",
                        "documentType": "RELEASE",
                        "requestingUser": "gernot.hillier@siemens.com",
                        "moderators": ["admin2@sw360.org", "thomas.graf@siemens.com"],
                        "documentName": "@grpc/grpc-js (1.9.15)",
                        "moderationState": "PENDING",
                        "requestingUserDepartment": "SI",
                        "componentType": "OSS",
                        "moderatorsSize": 157,
                        "_links": {
                            "self": {
                            "href": "https://my.server.com/resource/api/moderationrequest/b4"
                            }
                        }
                    }]
                },
                "_links": {
                    "first": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=0&page_entries=20"
                    },
                    "next": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=1&page_entries=20"
                    },
                    "last": {
                    "href": "https://my.server.com/resource/api/moderationrequest?page=2769&page_entries=20"
                    },
                    "curies": [
                    {
                        "href": "https://my.server.com/resource/docs/{rel}.html",
                        "name": "sw360",
                        "templated": true
                    }
                    ]
                },
                "page": {
                    "size": 20,
                    "totalElements": 5555,
                    "totalPages": 3333,
                    "number": 0
                }
            }''',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        mrs = lib.get_moderation_requests_by_state("open", True, page=2, page_size=8, sort="timestamp,desc")
        self.assertIsNotNone(mrs)
        self.assertTrue(len(mrs) > 0)
        mr_list = mrs["_embedded"]["sw360:moderationRequests"]
        self.assertEqual("@grpc/grpc-js (1.9.15)", mr_list[0]["documentName"])

    @responses.activate
    def test_get_license(self) -> None:
        lib = SW360(self.MYURL, self.MYTOKEN, False)
        self._add_login_response()
        actual = lib.login_api()
        self.assertTrue(actual)

        responses.add(
            method=responses.GET,
            url=self.MYURL + "resource/api/moderationrequest/0815",
            body='''{
                "id": "0815",
                "timestamp": 1729870771747,
                "timestampOfDecision": 0,
                "documentId": "8d101909d2f24ea592e666e9e9bb9eb0",
                "documentType": "RELEASE",
                "requestingUser": "gernot.hillier@siemens.com",
                "moderators": ["admin2@sw360.org", "thomas.graf@siemens.com"],
                "documentName": "@grpc/grpc-js (1.9.15)",
                "moderationState": "PENDING",
                "requestingUserDepartment": "SI",
                "componentType": "OSS",
                "moderatorsSize": 157,
                "_links": {
                "self": {
                    "href": "https://my.server.com/resource/api/moderationrequest/b41ddfb69b40439cabb18538313a036c"
                }
                }
            }''',
            status=200,
            content_type="application/json",
            adding_headers={"Authorization": "Token " + self.MYTOKEN},
        )

        mr = lib.get_moderation_request("0815")
        self.assertIsNotNone(license)
        if mr:  # only for mypy
            self.assertEqual("0815", mr["id"])
            self.assertEqual("@grpc/grpc-js (1.9.15)", mr["documentName"])


if __name__ == "__main__":
    unittest.main()
