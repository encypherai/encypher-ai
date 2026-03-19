# WordPressConnectCompletePayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** | Magic-link completion token |

## Example

```python
from encypher.models.word_press_connect_complete_payload import WordPressConnectCompletePayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressConnectCompletePayload from a JSON string
word_press_connect_complete_payload_instance = WordPressConnectCompletePayload.from_json(json)
# print the JSON string representation of the object
print(WordPressConnectCompletePayload.to_json())

# convert the object into a dict
word_press_connect_complete_payload_dict = word_press_connect_complete_payload_instance.to_dict()
# create an instance of WordPressConnectCompletePayload from a dict
word_press_connect_complete_payload_from_dict = WordPressConnectCompletePayload.from_dict(word_press_connect_complete_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
