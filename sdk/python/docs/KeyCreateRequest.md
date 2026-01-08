# KeyCreateRequest

Request to create a new API key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**permissions** | **List[str]** | Permissions: sign, verify, read, admin | [optional] [default to [sign, verify]]
**expires_in_days** | **int** |  | [optional] 

## Example

```python
from encypher.models.key_create_request import KeyCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of KeyCreateRequest from a JSON string
key_create_request_instance = KeyCreateRequest.from_json(json)
# print the JSON string representation of the object
print(KeyCreateRequest.to_json())

# convert the object into a dict
key_create_request_dict = key_create_request_instance.to_dict()
# create an instance of KeyCreateRequest from a dict
key_create_request_from_dict = KeyCreateRequest.from_dict(key_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


