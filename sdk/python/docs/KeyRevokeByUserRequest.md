# KeyRevokeByUserRequest

Request to revoke all keys for a specific user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | User ID whose keys should be revoked |

## Example

```python
from encypher.models.key_revoke_by_user_request import KeyRevokeByUserRequest

# TODO update the JSON string below
json = "{}"
# create an instance of KeyRevokeByUserRequest from a JSON string
key_revoke_by_user_request_instance = KeyRevokeByUserRequest.from_json(json)
# print the JSON string representation of the object
print(KeyRevokeByUserRequest.to_json())

# convert the object into a dict
key_revoke_by_user_request_dict = key_revoke_by_user_request_instance.to_dict()
# create an instance of KeyRevokeByUserRequest from a dict
key_revoke_by_user_request_from_dict = KeyRevokeByUserRequest.from_dict(key_revoke_by_user_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
