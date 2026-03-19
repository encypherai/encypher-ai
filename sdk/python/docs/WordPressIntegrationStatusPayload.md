# WordPressIntegrationStatusPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**install_id** | **str** |  | [optional]
**connection_status** | **str** | Current plugin connection state |
**site_url** | **str** |  | [optional]
**admin_url** | **str** |  | [optional]
**site_name** | **str** |  | [optional]
**environment** | **str** |  | [optional]
**network_id** | **str** |  | [optional]
**blog_id** | **int** |  | [optional]
**is_multisite** | **bool** |  | [optional]
**is_primary** | **bool** |  | [optional]
**organization_id** | **str** |  | [optional]
**organization_name** | **str** |  | [optional]
**plugin_version** | **str** |  | [optional]
**plugin_installed** | **bool** |  | [optional]
**connection_tested** | **bool** |  | [optional]
**last_connection_checked_at** | **str** |  | [optional]
**last_signed_at** | **str** |  | [optional]
**last_signed_post_id** | **int** |  | [optional]
**last_signed_post_url** | **str** |  | [optional]
**signed_post_count** | **int** |  | [optional]

## Example

```python
from encypher.models.word_press_integration_status_payload import WordPressIntegrationStatusPayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressIntegrationStatusPayload from a JSON string
word_press_integration_status_payload_instance = WordPressIntegrationStatusPayload.from_json(json)
# print the JSON string representation of the object
print(WordPressIntegrationStatusPayload.to_json())

# convert the object into a dict
word_press_integration_status_payload_dict = word_press_integration_status_payload_instance.to_dict()
# create an instance of WordPressIntegrationStatusPayload from a dict
word_press_integration_status_payload_from_dict = WordPressIntegrationStatusPayload.from_dict(word_press_integration_status_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
