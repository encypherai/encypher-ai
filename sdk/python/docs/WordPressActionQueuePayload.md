# WordPressActionQueuePayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action_type** | **str** | Queued action to execute on the install |
**note** | **str** |  | [optional]

## Example

```python
from encypher.models.word_press_action_queue_payload import WordPressActionQueuePayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressActionQueuePayload from a JSON string
word_press_action_queue_payload_instance = WordPressActionQueuePayload.from_json(json)
# print the JSON string representation of the object
print(WordPressActionQueuePayload.to_json())

# convert the object into a dict
word_press_action_queue_payload_dict = word_press_action_queue_payload_instance.to_dict()
# create an instance of WordPressActionQueuePayload from a dict
word_press_action_queue_payload_from_dict = WordPressActionQueuePayload.from_dict(word_press_action_queue_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
