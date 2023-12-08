# -------------------------------------------------------------------------------
# Copyright (c) 2019-2023 Siemens
# All Rights Reserved.
# Author: thomas.graf@siemens.com
#
# Licensed under the MIT license.
# SPDX-License-Identifier: MIT
# -------------------------------------------------------------------------------

"""
Check a project on SW360
usage: check_project.py [-h] [-n NAME] [-v VERSION] [-id PROJECT_ID]
                        [-t SW360_TOKEN] [-url SW360_URL]

Check a project on SW360, display component clearing status

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  name of the project
  -v VERSION, --version VERSION
                        version of the project
  -id PROJECT_ID        SW360 id of the project, supersedes name and version
                        parameters
  -t SW360_TOKEN, --token SW360_TOKEN
                        use this token for access to SW360
  -url SW360_URL        use this URL for access to SW360

Examples

Productive system:
python check_project.py -n tr-card -v 1.0

Staging system:
python check_project.py -n tr-card -v 1.0 -t <token> -url https://stage.sw360.siemens.com
"""

import argparse
import os
import sys
from typing import Any, Dict, Optional

import requests
from colorama import Fore, Style, init

import sw360

# Do you use an oauth flow? This is usually False if you get your SW360 token
# in the SW360 preferences and true if you get it via a separate OAuth2 flow
OAUTH2 = False

# initialize colorama
init()


class CheckProject():
    """Check a project on SW360, display component clearing status"""
    def __init__(self) -> None:
        self.client: sw360.SW360
        self.project_id: str = ""
        self.sw360_url: str = "https://sw360.siemens.com"

    @classmethod
    def get_clearing_state(cls, proj: Dict[Any, Any], href: str) -> str | None:
        """Returns the clearing state of the given component/release"""
        if "linkedReleases" not in proj:
            return None

        rel = proj["linkedReleases"]
        for key in rel:
            if key["release"] == href:
                return key["mainlineState"]

        return None

    def has_source_code(self, href: str) -> bool:
        """Returns true if a source code attachment is available"""
        rel = self.client.get_release_by_url(href)
        if not rel:
            return False

        if "_embedded" not in rel:
            return False

        if "sw360:attachments" not in rel["_embedded"]:
            return False

        att = rel["_embedded"]["sw360:attachments"]
        for key in att:
            if key["attachmentType"] == "SOURCE":
                return True

        return False

    def show_linked_projects(self, project: Dict[Any, Any]) -> None:
        """Show linked projects of the given project"""
        if "_embedded" not in project:
            return

        if "sw360:projects" in project["_embedded"]:
            linked_projects = project["_embedded"]["sw360:projects"]
            if linked_projects:
                print("\n  Linked projects: ")
                for key in linked_projects:
                    print("    " + key["name"] + ", " + key["version"])
        else:
            print("\n    No linked projects")

    def show_linked_releases(self, project: Dict[Any, Any]) -> None:
        """Show linked releases of the given project"""
        if "_embedded" not in project:
            return

        if "sw360:releases" in project["_embedded"]:
            print("\n  Components: ")
            releases = project["_embedded"]["sw360:releases"]
            releases.sort(key=lambda s: s["name"].lower())
            for key in releases:
                href = key["_links"]["self"]["href"]
                state = self.get_clearing_state(project, href)
                prereq = ""
                if state == "OPEN":
                    print(Fore.LIGHTYELLOW_EX, end="", flush=True)
                    if not self.has_source_code(href):
                        print(Fore.LIGHTRED_EX, end="", flush=True)
                        prereq = "; No source provided"
                else:
                    prereq = ""

                print("    " + key["name"] + "; " + key["version"] + "; "
                      + state + prereq + Fore.RESET)
        else:
            print("    No linked releases")

    def show_project_status(self, project_id: str) -> None:
        """Retrieve and display project status"""
        try:
            project = self.client.get_project(project_id)
        except sw360.SW360Error as swex:
            print(Fore.LIGHTRED_EX + "  ERROR: unable to access project!")
            sys.exit("  " + str(swex) + Style.RESET_ALL)

        if not project:
            print("  Project not found!")
            return

        print("  Project name: " + project["name"] + ", " + project["version"])
        if "projectResponsible" in project:
            print("  Project responsible: " + project["projectResponsible"])
        print("  Project owner: " + project["projectOwner"])
        print("  Clearing state: " + project["clearingState"])

        self.show_linked_projects(project)
        self.show_linked_releases(project)

    def login(self, token: Optional[str] = None, url: Optional[str] = None) -> bool | sw360.SW360Error:
        """Login to SW360"""
        if token:
            sw360_api_token = token
        else:
            sw360_api_token = os.environ["SW360ProductionToken"]

        if url:
            self.sw360_url = url

        if self.sw360_url[-1] != "/":
            self.sw360_url += "/"

        if not sw360_api_token:
            sys.exit(Fore.LIGHTRED_EX + "  No SW360 API token specified!" + Style.RESET_ALL)

        self.client = sw360.SW360(self.sw360_url, sw360_api_token, oauth2=OAUTH2)

        try:
            result = self.client.login_api()
            return result
        except sw360.SW360Error as swex:
            if swex.response and (swex.response.status_code == requests.codes['unauthorized']):
                sys.exit(
                    Fore.LIGHTRED_EX +
                    "  You are not authorized!" +
                    Style.RESET_ALL)
            else:
                sys.exit(
                    Fore.LIGHTRED_EX +
                    "  Error authorizing user!" +
                    Style.RESET_ALL)

    def find_project(self, name: str, version: str) -> str:
        """Find the project with the matching name and version on SW360"""
        projects = self.client.get_projects_by_name(name)
        if not projects:
            sys.exit(Fore.YELLOW + "  No matching project found!" + Style.RESET_ALL)

        print("  Searching for projects")
        for project in projects:
            href = project["_links"]["self"]["href"]
            if "version" not in project:
                print(
                    "    "
                    + project["name"]
                    + " => ID = "
                    + self.client.get_id_from_href(href)
                )
            else:
                pid = self.client.get_id_from_href(href)
                print(
                    "    "
                    + project["name"]
                    + ", "
                    + project["version"]
                    + " => ID = "
                    + pid
                )
                if project["version"].lower() == version:
                    return pid

        return ""

    @classmethod
    def parse_commandline(cls) -> Any:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="Check a project on SW360, display component clearing status"
        )
        parser.add_argument("-n", "--name", help="name of the project")
        parser.add_argument("-v", "--version", help="version of the project")
        parser.add_argument(
            "-id",
            dest="project_id",
            help="SW360 id of the project, supersedes name and version parameters",
        )
        parser.add_argument(
            "-t",
            "--token",
            dest="sw360_token",
            help="use this token for access to SW360",
        )
        parser.add_argument(
            "-url", dest="sw360_url", help="use this URL for access to SW360"
        )

        args = parser.parse_args()

        if not args.project_id:
            if not args.name:
                sys.exit(Fore.LIGHTRED_EX + "  No project name specified!" + Style.RESET_ALL)
            if not args.version:
                sys.exit(Fore.LIGHTRED_EX + "  No project version specified!" + Style.RESET_ALL)

        return args

    def main(self) -> None:
        """Main method"""
        print("\nCheck a project on SW360")

        args = self.parse_commandline()

        self.login(token=args.sw360_token, url=args.sw360_url)

        if args.project_id:
            self.project_id = args.project_id
        else:
            self.project_id = self.find_project(args.name, args.version)

        if not self.project_id:
            sys.exit(Fore.LIGHTRED_EX + "  ERROR: no (unique) project found!" + Style.RESET_ALL)

        print("")
        self.show_project_status(self.project_id)


if __name__ == "__main__":
    APP = CheckProject()
    APP.main()
