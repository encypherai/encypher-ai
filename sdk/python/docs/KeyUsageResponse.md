# KeyUsageResponse

Response with key usage statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  |

## Example

```python
from encypher.models.key_usage_response import KeyUsageResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyUsageResponse from a JSON string
key_usage_response_instance = KeyUsageResponse.from_json(json)
# print the JSON string representation of the object
print(KeyUsageResponse.to_json())

# convert the object into a dict
key_usage_response_dict = key_usage_response_instance.to_dict()
# create an instance of KeyUsageResponse from a dict
key_usage_response_from_dict = KeyUsageResponse.from_dict(key_usage_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
