# AccountInfo

Organization account information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** | Organization ID |
**name** | **str** | Organization name |
**email** | **str** |  | [optional]
**tier** | **str** | Subscription tier |
**features** | [**FeatureFlags**](FeatureFlags.md) | Enabled features |
**publisher_display_name** | **str** |  | [optional]
**anonymous_publisher** | **bool** | Whether publisher identity is anonymized in verification | [optional] [default to False]
**created_at** | **str** |  | [optional]
**subscription_status** | **str** | Subscription status | [optional] [default to 'active']

## Example

```python
from encypher.models.account_info import AccountInfo

# TODO update the JSON string below
json = "{}"
# create an instance of AccountInfo from a JSON string
account_info_instance = AccountInfo.from_json(json)
# print the JSON string representation of the object
print(AccountInfo.to_json())

# convert the object into a dict
account_info_dict = account_info_instance.to_dict()
# create an instance of AccountInfo from a dict
account_info_from_dict = AccountInfo.from_dict(account_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
