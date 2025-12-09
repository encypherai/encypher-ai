# UsageMetric

Single usage metric with limit info.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**used** | **int** |  | 
**limit** | **int** |  | 
**remaining** | **int** |  | 
**percentage_used** | **float** |  | 
**available** | **bool** |  | 

## Example

```python
from encypher.models.usage_metric import UsageMetric

# TODO update the JSON string below
json = "{}"
# create an instance of UsageMetric from a JSON string
usage_metric_instance = UsageMetric.from_json(json)
# print the JSON string representation of the object
print(UsageMetric.to_json())

# convert the object into a dict
usage_metric_dict = usage_metric_instance.to_dict()
# create an instance of UsageMetric from a dict
usage_metric_from_dict = UsageMetric.from_dict(usage_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


