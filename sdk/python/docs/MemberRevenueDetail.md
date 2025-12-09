# MemberRevenueDetail

Schema for member revenue detail.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**member_id** | **str** |  | 
**content_count** | **int** |  | 
**access_count** | **int** |  | 
**revenue_amount** | **str** |  | 
**status** | [**PayoutStatus**](PayoutStatus.md) |  | 
**paid_at** | **datetime** |  | 
**payment_reference** | **str** |  | 

## Example

```python
from encypher.models.member_revenue_detail import MemberRevenueDetail

# TODO update the JSON string below
json = "{}"
# create an instance of MemberRevenueDetail from a JSON string
member_revenue_detail_instance = MemberRevenueDetail.from_json(json)
# print the JSON string representation of the object
print(MemberRevenueDetail.to_json())

# convert the object into a dict
member_revenue_detail_dict = member_revenue_detail_instance.to_dict()
# create an instance of MemberRevenueDetail from a dict
member_revenue_detail_from_dict = MemberRevenueDetail.from_dict(member_revenue_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


