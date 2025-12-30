# KeyRevokeResponse

Response after revoking a key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | **Dict[str, object]** |  | 

## Example

```python
from encypher.models.key_revoke_response import KeyRevokeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of KeyRevokeResponse from a JSON string
key_revoke_response_instance = KeyRevokeResponse.from_json(json)
# print the JSON string representation of the object
print(KeyRevokeResponse.to_json())

# convert the object into a dict
key_revoke_response_dict = key_revoke_response_instance.to_dict()
# create an instance of KeyRevokeResponse from a dict
key_revoke_response_from_dict = KeyRevokeResponse.from_dict(key_revoke_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


