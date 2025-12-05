# UsageResetResponse

Response after resetting usage counters.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | 
**message** | **str** |  | 
**organization_id** | **str** |  | 
**reset_at** | **str** |  | 

## Example

```python
from encypher.models.usage_reset_response import UsageResetResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UsageResetResponse from a JSON string
usage_reset_response_instance = UsageResetResponse.from_json(json)
# print the JSON string representation of the object
print(UsageResetResponse.to_json())

# convert the object into a dict
usage_reset_response_dict = usage_reset_response_instance.to_dict()
# create an instance of UsageResetResponse from a dict
usage_reset_response_from_dict = UsageResetResponse.from_dict(usage_reset_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


