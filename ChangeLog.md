<!--
# SPDX-FileCopyrightText: (c) 2019-2023 Siemens
# SPDX-License-Identifier: MIT
-->

# SW360 Base Library for Python

## V1.2.3

* `get_projects` fixed - paging work now as expected.
* `get_projects` now also supports a sort order.

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
  * Debug option to supress session handling.
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
  and different attchment types.

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
