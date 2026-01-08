# KeyUpdateResponse

Response after updating a key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.key_update_response import KeyUpdateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyUpdateResponse from a JSON string
key_update_response_instance = KeyUpdateResponse.from_json(json)
# print the JSON string representation of the object
print(KeyUpdateResponse.to_json())

# convert the object into a dict
key_update_response_dict = key_update_response_instance.to_dict()
# create an instance of KeyUpdateResponse from a dict
key_update_response_from_dict = KeyUpdateResponse.from_dict(key_update_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


