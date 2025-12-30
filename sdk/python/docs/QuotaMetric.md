# QuotaMetric

Single quota metric.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Human-readable metric name | 
**used** | **int** | Amount used this period | 
**limit** | **int** | Period limit (-1 for unlimited) | 
**remaining** | **int** | Amount remaining (-1 for unlimited) | 
**percentage_used** | **float** | Percentage of limit used | 

## Example

```python
from encypher.models.quota_metric import QuotaMetric

# TODO update the JSON string below
json = "{}"
# create an instance of QuotaMetric from a JSON string
quota_metric_instance = QuotaMetric.from_json(json)
# print the JSON string representation of the object
print(QuotaMetric.to_json())

# convert the object into a dict
quota_metric_dict = quota_metric_instance.to_dict()
# create an instance of QuotaMetric from a dict
quota_metric_from_dict = QuotaMetric.from_dict(quota_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


