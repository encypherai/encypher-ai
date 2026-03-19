# WordPressConnectPollResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  |

## Example

```python
from encypher.models.word_press_connect_poll_response import WordPressConnectPollResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WordPressConnectPollResponse from a JSON string
word_press_connect_poll_response_instance = WordPressConnectPollResponse.from_json(json)
# print the JSON string representation of the object
print(WordPressConnectPollResponse.to_json())

# convert the object into a dict
word_press_connect_poll_response_dict = word_press_connect_poll_response_instance.to_dict()
# create an instance of WordPressConnectPollResponse from a dict
word_press_connect_poll_response_from_dict = WordPressConnectPollResponse.from_dict(word_press_connect_poll_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
