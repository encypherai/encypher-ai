# AutoProvisionResponse

Response schema for auto-provisioning.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether provisioning was successful | 
**message** | **str** | Success or error message | 
**organization_id** | **str** | Created organization ID | 
**organization_name** | **str** | Organization name | 
**user_id** | **str** |  | [optional] 
**api_key** | [**APIKeyResponse**](APIKeyResponse.md) | Generated API key | 
**tier** | **str** | Organization tier | 
**features_enabled** | **Dict[str, bool]** | Enabled features | 
**quota_limits** | **Dict[str, int]** | Quota limits | 
**next_steps** | **Dict[str, str]** | Next steps and documentation links | 

## Example

```python
from encypher.models.auto_provision_response import AutoProvisionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AutoProvisionResponse from a JSON string
auto_provision_response_instance = AutoProvisionResponse.from_json(json)
# print the JSON string representation of the object
print(AutoProvisionResponse.to_json())

# convert the object into a dict
auto_provision_response_dict = auto_provision_response_instance.to_dict()
# create an instance of AutoProvisionResponse from a dict
auto_provision_response_from_dict = AutoProvisionResponse.from_dict(auto_provision_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


