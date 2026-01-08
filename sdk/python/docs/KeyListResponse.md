# KeyListResponse

Response for key listing.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.key_list_response import KeyListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyListResponse from a JSON string
key_list_response_instance = KeyListResponse.from_json(json)
# print the JSON string representation of the object
print(KeyListResponse.to_json())

# convert the object into a dict
key_list_response_dict = key_list_response_instance.to_dict()
# create an instance of KeyListResponse from a dict
key_list_response_from_dict = KeyListResponse.from_dict(key_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


