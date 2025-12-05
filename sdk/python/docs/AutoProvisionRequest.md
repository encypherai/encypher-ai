# AutoProvisionRequest

Request schema for auto-provisioning an organization and API key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | User email address | 
**organization_name** | **str** |  | [optional] 
**source** | **str** | Source of the provisioning request | 
**source_metadata** | **Dict[str, object]** |  | [optional] 
**tier** | **str** |  | [optional] 
**auto_activate** | **bool** | Whether to automatically activate the organization | [optional] [default to True]

## Example

```python
from encypher.models.auto_provision_request import AutoProvisionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AutoProvisionRequest from a JSON string
auto_provision_request_instance = AutoProvisionRequest.from_json(json)
# print the JSON string representation of the object
print(AutoProvisionRequest.to_json())

# convert the object into a dict
auto_provision_request_dict = auto_provision_request_instance.to_dict()
# create an instance of AutoProvisionRequest from a dict
auto_provision_request_from_dict = AutoProvisionRequest.from_dict(auto_provision_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


