# QuotaInfo

Detailed quota information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  | 
**tier** | **str** |  | 
**period_start** | **str** |  | 
**period_end** | **str** |  | 
**metrics** | [**Dict[str, QuotaMetric]**](QuotaMetric.md) |  | 
**reset_date** | **str** |  | 

## Example

```python
from encypher.models.quota_info import QuotaInfo

# TODO update the JSON string below
json = "{}"
# create an instance of QuotaInfo from a JSON string
quota_info_instance = QuotaInfo.from_json(json)
# print the JSON string representation of the object
print(QuotaInfo.to_json())

# convert the object into a dict
quota_info_dict = quota_info_instance.to_dict()
# create an instance of QuotaInfo from a dict
quota_info_from_dict = QuotaInfo.from_dict(quota_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


