# RevenueDistributionCreate

Schema for creating a revenue distribution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agreement_id** | **str** |  | 
**period_start** | **date** |  | 
**period_end** | **date** |  | 

## Example

```python
from encypher.models.revenue_distribution_create import RevenueDistributionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RevenueDistributionCreate from a JSON string
revenue_distribution_create_instance = RevenueDistributionCreate.from_json(json)
# print the JSON string representation of the object
print(RevenueDistributionCreate.to_json())

# convert the object into a dict
revenue_distribution_create_dict = revenue_distribution_create_instance.to_dict()
# create an instance of RevenueDistributionCreate from a dict
revenue_distribution_create_from_dict = RevenueDistributionCreate.from_dict(revenue_distribution_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


