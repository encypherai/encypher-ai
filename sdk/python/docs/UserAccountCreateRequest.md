# UserAccountCreateRequest

Request schema for creating a user account.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | User email address | 
**full_name** | **str** |  | [optional] 
**organization_id** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**send_welcome_email** | **bool** | Whether to send welcome email | [optional] [default to True]

## Example

```python
from encypher.models.user_account_create_request import UserAccountCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UserAccountCreateRequest from a JSON string
user_account_create_request_instance = UserAccountCreateRequest.from_json(json)
# print the JSON string representation of the object
print(UserAccountCreateRequest.to_json())

# convert the object into a dict
user_account_create_request_dict = user_account_create_request_instance.to_dict()
# create an instance of UserAccountCreateRequest from a dict
user_account_create_request_from_dict = UserAccountCreateRequest.from_dict(user_account_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


