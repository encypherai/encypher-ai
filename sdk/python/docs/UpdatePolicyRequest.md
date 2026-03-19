# UpdatePolicyRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional]
**description** | **str** |  | [optional]
**enforcement** | **str** |  | [optional]
**scope** | **str** |  | [optional]
**rules** | [**List[PolicyRule]**](PolicyRule.md) |  | [optional]
**active** | **bool** |  | [optional]

## Example

```python
from encypher.models.update_policy_request import UpdatePolicyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePolicyRequest from a JSON string
update_policy_request_instance = UpdatePolicyRequest.from_json(json)
# print the JSON string representation of the object
print(UpdatePolicyRequest.to_json())

# convert the object into a dict
update_policy_request_dict = update_policy_request_instance.to_dict()
# create an instance of UpdatePolicyRequest from a dict
update_policy_request_from_dict = UpdatePolicyRequest.from_dict(update_policy_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
