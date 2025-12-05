# UserAccountResponse

Response schema for user account.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | User identifier | 
**email** | **str** | User email | 
**full_name** | **str** |  | [optional] 
**organization_id** | **str** | Associated organization | 
**role** | **str** | User role | 
**created_at** | **datetime** | Creation timestamp | 
**is_active** | **bool** | Whether account is active | 

## Example

```python
from encypher.models.user_account_response import UserAccountResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UserAccountResponse from a JSON string
user_account_response_instance = UserAccountResponse.from_json(json)
# print the JSON string representation of the object
print(UserAccountResponse.to_json())

# convert the object into a dict
user_account_response_dict = user_account_response_instance.to_dict()
# create an instance of UserAccountResponse from a dict
user_account_response_from_dict = UserAccountResponse.from_dict(user_account_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


