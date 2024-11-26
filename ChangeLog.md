<!--
# SPDX-FileCopyrightText: (c) 2019-2024 Siemens
# SPDX-License-Identifier: MIT
-->

# SW360 Base Library for Python

## Upcoming Release

* Update `get_all_releases` to include `isNewClearingWithSourceAvailable` parameter:
  * This parameter allows filtering releases that are in the **new clearing** state and have
    the source available.
  * This feature is yet to be released in the new version of SW360.

## V1.7.0

* more REST API endpoints implemented:
  * `get_recent_releases`
  * `get_recent_components`
  * `get_all_moderation_requests`
  * `get_moderation_requests_by_state`
  * `get_moderation_request`

## V1.6.0

* packages REST API calls implemented.
* unit test `test_login_failed_invalid_url` disabled because it delays all tests.
* have unit tests for packages.
* have more test coverage.

## V1.5.1

* update requests 2.31.0 => 2.32.2 to fix CVE-2024-35195.
* update transient dependencies.

## V1.5.0

* when using CaPyCLI in a CI pipeline, connection problems to the SW360 server (5xx) cause
  the pipeline to fail. We have now add an improved session handling to all api requests.
* dependency updates due to security vulnerabilities in `idna`.

## V1.4.1

* fix for `update_project`: ensure that there is no key error.
* dependency updates.

## V1.4.0

* have type hints.
* drop support for Python 3.7.
* dependency update (urllib3 (1.26.18 -> 2.0.7), etc.).

## V1.3.1

* dependency updates to fix security vulnerabilities.

## V1.3.0

* `get_projects` fixed - paging work now as expected.
* `get_projects` now also supports a sort order.
* `get_all_releases` now also support paging.
  **IMPORTANT:** Due to compatibility reasons `get_all_releases` without `page` parameter returns
  a list of releases. But when the `page` parameter is used, a dict will be returned that also contains
  information about paging.
* `get_all_components` now supports `allDetails` and `sort`.
  **IMPORTANT:** Due to compatibility reasons `get_all_components` without `page` parameter returns
  a list of components. But when the `page` parameter is used, a dict will be returned that also contains
  information about paging.  

## V1.2.2

* fix: download_xxx_attachment now raises an SW360Error for failed downloads
  instead of silently creating a file containing the JSON answer
* dependency updates to fix requests CVE-2023-32681.
* be REUSE compliant.
* get rid of json_params_matcher deprecation warning.

## V1.2.1

* dependency updates to mitigate potential security vulnerabilities.
* markdown style checks introduced.
* logging introduced, especially to show a warning when adding an attachment  
  returns is not 201 (created) but 202 (accepted).

## V1.2.0

* new method `update_project_release_relationship`.
* original get_health_status() endpoint URL has been restored by the SW360 team.
* fix: better check assumptions on returned data, see https://github.com/sw360/sw360python/issues/5.
* `update_project` has a new parameter `add_subprojects` to only **add** the new
  sub-projects and not to overwrite all existing sub-projects.

## V1.1.0

* New method `duplicate_project` to create a copy of an existing project.

## V1.0.0

* **New Features**:
  * `get_projects_by_tag` added.
  * `get_releases_by_name` added.
  * `get_all_vendors` added.
* We have covered nearly all of the possible REST API calls.  
  The library is successfully being used by multiple projects.  
  Time to release version 1.0.0.

## V0.9.1

* **New Features**:
  * support to retrieve information about clearing requests (`get_clearing_request`,  
  `get_clearing_request_for_project`).

## V0.9

* relicensed to MIT.
* **Breaking API changes**:
  * create_new_{component,release,project} now have parameters for required attributes
  * drop support for dump_rest_call() and dump_rest_call_to_file().
  * upload_attachment() has been renamed to upload_release_attachment(). This is to have  
    the same naming scheme for the new methods upload_component_attachment() and  
    upload_project_attachment().
* **New Features**:
  * support of the group parameter for the /projects endpoint.
  * SW360 REST API now support project fields 'Project state' and 'Phase-out since'.
  * get_health_status() added.
  * get_project_vulnerabilities() added.
  * SW360Error has new property `details`.
* **Improvements**:
  * Debug option to suppress session handling.
  * unit tests added.
* published on GitHub.

## V0.5 (2020-04-16)

* rename parameters for methods get_{release,component}_by_external_id
  to align with documentation and with get_projects_by_external_id
  * id_type->ext_id_name
  * id_value->ext_id_value
* rename methods to plural form as they all return list of objects:
  * get_release_by_external_id -> get_releases_by_external_id
  * get_component_by_external_id -> get_components_by_external_id
* switch to [poetry](https://python-poetry.org/) build tool. This has no
  effect on end users of this library, but simplifies development.
* remove requirement for colorama, relax other required versions
* new methods:
  * update_{project,component,release}_external_id()
  * close_api()
* The login_api() method doesn't require `token` parameter any more.
* slightly fix signatures of get_attachment_infos_*() methods to clarify
  they provide information about all attachments of a given resource/hash.
* change get_attachment() method to retrieve data of single attachment
* update_project_releases(): rename `project` parameter to `releases`,
  new parameter `add` to add releases

## V0.4 (2019-11-12)

* improved error handling
* new methods
  * get_users_of_project
  * get_users_of_component
  * get_users_of_release
* upload_attachment() has been tested with different file types
  and different attachment types.

## V0.3 (2019-09-24)

* fix in get_component_by_url().
* support for OAuth2 tokens.
* new methods
  * get_projects_by_external_id()
  * get_component_by_external_id
  * get_all_vulnerabilities()
  * get_vulnerability()
  * get_all_licenses()
  * get_license()
  * download_license_info()
  * get_project_releases()

## V0.2 (2019-08-27)

* first version available a separate project on code.siemens.com.

## V0.1 (2019-4-18)

* first version available on BT-Artifactory.
