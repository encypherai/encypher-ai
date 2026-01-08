# KeyUpdateRequest

Request to update a key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**permissions** | **List[str]** |  | [optional] 

## Example

```python
from encypher.models.key_update_request import KeyUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of KeyUpdateRequest from a JSON string
key_update_request_instance = KeyUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(KeyUpdateRequest.to_json())

# convert the object into a dict
key_update_request_dict = key_update_request_instance.to_dict()
# create an instance of KeyUpdateRequest from a dict
key_update_request_from_dict = KeyUpdateRequest.from_dict(key_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


