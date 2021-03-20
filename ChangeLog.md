# SW360 Base Library for Python

## NEXT
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

## V0.2	(2019-08-27)
* first version available a separate project on code.siemens.com.

## V0.1 (2019-4-18)
* first version available on BT-Artifactory.
