# WordPressActionAckPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Acknowledged action status |
**result_message** | **str** |  | [optional]
**completed_at** | **str** |  | [optional]

## Example

```python
from encypher.models.word_press_action_ack_payload import WordPressActionAckPayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressActionAckPayload from a JSON string
word_press_action_ack_payload_instance = WordPressActionAckPayload.from_json(json)
# print the JSON string representation of the object
print(WordPressActionAckPayload.to_json())

# convert the object into a dict
word_press_action_ack_payload_dict = word_press_action_ack_payload_instance.to_dict()
# create an instance of WordPressActionAckPayload from a dict
word_press_action_ack_payload_from_dict = WordPressActionAckPayload.from_dict(word_press_action_ack_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
