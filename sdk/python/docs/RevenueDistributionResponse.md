# RevenueDistributionResponse

Schema for revenue distribution response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**agreement_id** | **str** |  | 
**period_start** | **date** |  | 
**period_end** | **date** |  | 
**total_revenue** | **str** |  | 
**encypher_share** | **str** |  | 
**member_pool** | **str** |  | 
**status** | [**DistributionStatus**](DistributionStatus.md) |  | 
**created_at** | **datetime** |  | 
**processed_at** | **datetime** |  | 
**member_revenues** | [**List[MemberRevenueDetail]**](MemberRevenueDetail.md) |  | [optional] 

## Example

```python
from encypher.models.revenue_distribution_response import RevenueDistributionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RevenueDistributionResponse from a JSON string
revenue_distribution_response_instance = RevenueDistributionResponse.from_json(json)
# print the JSON string representation of the object
print(RevenueDistributionResponse.to_json())

# convert the object into a dict
revenue_distribution_response_dict = revenue_distribution_response_instance.to_dict()
# create an instance of RevenueDistributionResponse from a dict
revenue_distribution_response_from_dict = RevenueDistributionResponse.from_dict(revenue_distribution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


