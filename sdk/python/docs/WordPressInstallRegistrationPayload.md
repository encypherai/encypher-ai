# WordPressInstallRegistrationPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**install_id** | **str** |  | [optional]
**site_url** | **str** |  | [optional]
**admin_url** | **str** |  | [optional]
**site_name** | **str** |  | [optional]
**environment** | **str** |  | [optional]
**network_id** | **str** |  | [optional]
**blog_id** | **int** |  | [optional]
**is_multisite** | **bool** |  | [optional]
**is_primary** | **bool** |  | [optional]
**plugin_version** | **str** |  | [optional]

## Example

```python
from encypher.models.word_press_install_registration_payload import WordPressInstallRegistrationPayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressInstallRegistrationPayload from a JSON string
word_press_install_registration_payload_instance = WordPressInstallRegistrationPayload.from_json(json)
# print the JSON string representation of the object
print(WordPressInstallRegistrationPayload.to_json())

# convert the object into a dict
word_press_install_registration_payload_dict = word_press_install_registration_payload_instance.to_dict()
# create an instance of WordPressInstallRegistrationPayload from a dict
word_press_install_registration_payload_from_dict = WordPressInstallRegistrationPayload.from_dict(word_press_install_registration_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
