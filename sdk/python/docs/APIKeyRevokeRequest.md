# APIKeyRevokeRequest

Request schema for revoking an API key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key_id** | **str** | API key identifier to revoke | 
**reason** | **str** |  | [optional] 

## Example

```python
from encypher.models.api_key_revoke_request import APIKeyRevokeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of APIKeyRevokeRequest from a JSON string
api_key_revoke_request_instance = APIKeyRevokeRequest.from_json(json)
# print the JSON string representation of the object
print(APIKeyRevokeRequest.to_json())

# convert the object into a dict
api_key_revoke_request_dict = api_key_revoke_request_instance.to_dict()
# create an instance of APIKeyRevokeRequest from a dict
api_key_revoke_request_from_dict = APIKeyRevokeRequest.from_dict(api_key_revoke_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


