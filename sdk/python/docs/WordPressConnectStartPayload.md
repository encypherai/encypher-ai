# WordPressConnectStartPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  |
**install_id** | **str** |  | [optional]
**site_url** | **str** |  | [optional]
**admin_url** | **str** |  | [optional]
**site_name** | **str** |  | [optional]
**environment** | **str** |  | [optional]
**api_base_url** | **str** |  | [optional]

## Example

```python
from encypher.models.word_press_connect_start_payload import WordPressConnectStartPayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressConnectStartPayload from a JSON string
word_press_connect_start_payload_instance = WordPressConnectStartPayload.from_json(json)
# print the JSON string representation of the object
print(WordPressConnectStartPayload.to_json())

# convert the object into a dict
word_press_connect_start_payload_dict = word_press_connect_start_payload_instance.to_dict()
# create an instance of WordPressConnectStartPayload from a dict
word_press_connect_start_payload_from_dict = WordPressConnectStartPayload.from_dict(word_press_connect_start_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
