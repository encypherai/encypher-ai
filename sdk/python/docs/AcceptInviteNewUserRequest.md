# AcceptInviteNewUserRequest

Payload for accepting a team invite as a brand-new user.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  |
**password** | **str** |  |

## Example

```python
from encypher.models.accept_invite_new_user_request import AcceptInviteNewUserRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AcceptInviteNewUserRequest from a JSON string
accept_invite_new_user_request_instance = AcceptInviteNewUserRequest.from_json(json)
# print the JSON string representation of the object
print(AcceptInviteNewUserRequest.to_json())

# convert the object into a dict
accept_invite_new_user_request_dict = accept_invite_new_user_request_instance.to_dict()
# create an instance of AcceptInviteNewUserRequest from a dict
accept_invite_new_user_request_from_dict = AcceptInviteNewUserRequest.from_dict(accept_invite_new_user_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
