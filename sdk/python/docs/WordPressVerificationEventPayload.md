# WordPressVerificationEventPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**install_id** | **str** | Stable install ID for a WordPress property |
**post_id** | **int** |  | [optional]
**post_url** | **str** |  | [optional]
**valid** | **bool** | Whether verification succeeded | [optional] [default to False]
**tampered** | **bool** | Whether content appeared tampered | [optional] [default to False]
**status** | **str** |  | [optional]
**verified_at** | **str** |  | [optional]
**source** | **str** | Event source | [optional] [default to 'wordpress_plugin']

## Example

```python
from encypher.models.word_press_verification_event_payload import WordPressVerificationEventPayload

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressVerificationEventPayload from a JSON string
word_press_verification_event_payload_instance = WordPressVerificationEventPayload.from_json(json)
# print the JSON string representation of the object
print(WordPressVerificationEventPayload.to_json())

# convert the object into a dict
word_press_verification_event_payload_dict = word_press_verification_event_payload_instance.to_dict()
# create an instance of WordPressVerificationEventPayload from a dict
word_press_verification_event_payload_from_dict = WordPressVerificationEventPayload.from_dict(word_press_verification_event_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
