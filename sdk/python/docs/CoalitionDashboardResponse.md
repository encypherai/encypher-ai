# CoalitionDashboardResponse

Coalition dashboard data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  | 
**tier** | **str** |  | 
**publisher_share_percent** | **int** |  | 
**coalition_member** | **bool** |  | 
**opted_out** | **bool** |  | 
**current_period** | [**ContentStats**](ContentStats.md) |  | 
**lifetime_earnings_cents** | **int** |  | 
**pending_earnings_cents** | **int** |  | 
**paid_earnings_cents** | **int** |  | 
**recent_earnings** | [**List[EarningsSummary]**](EarningsSummary.md) |  | 
**recent_payouts** | [**List[PayoutSummary]**](PayoutSummary.md) |  | 

## Example

```python
from encypher.models.coalition_dashboard_response import CoalitionDashboardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CoalitionDashboardResponse from a JSON string
coalition_dashboard_response_instance = CoalitionDashboardResponse.from_json(json)
# print the JSON string representation of the object
print(CoalitionDashboardResponse.to_json())

# convert the object into a dict
coalition_dashboard_response_dict = coalition_dashboard_response_instance.to_dict()
# create an instance of CoalitionDashboardResponse from a dict
coalition_dashboard_response_from_dict = CoalitionDashboardResponse.from_dict(coalition_dashboard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


