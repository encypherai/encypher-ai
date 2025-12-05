# AppRoutersToolsVerifyVerdict

Verification verdict details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  | [optional] [default to False]
**tampered** | **bool** |  | [optional] [default to False]
**reason_code** | **str** |  | [optional] [default to 'UNKNOWN']
**signer_id** | **str** |  | [optional] 
**signer_name** | **str** |  | [optional] 
**timestamp** | **str** |  | [optional] 

## Example

```python
from encypher.models.app_routers_tools_verify_verdict import AppRoutersToolsVerifyVerdict

# TODO update the JSON string below
json = "{}"
# create an instance of AppRoutersToolsVerifyVerdict from a JSON string
app_routers_tools_verify_verdict_instance = AppRoutersToolsVerifyVerdict.from_json(json)
# print the JSON string representation of the object
print(AppRoutersToolsVerifyVerdict.to_json())

# convert the object into a dict
app_routers_tools_verify_verdict_dict = app_routers_tools_verify_verdict_instance.to_dict()
# create an instance of AppRoutersToolsVerifyVerdict from a dict
app_routers_tools_verify_verdict_from_dict = AppRoutersToolsVerifyVerdict.from_dict(app_routers_tools_verify_verdict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


