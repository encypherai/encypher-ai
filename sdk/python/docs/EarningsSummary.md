# EarningsSummary

Earnings summary for a period.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period_start** | **str** |  | 
**period_end** | **str** |  | 
**gross_revenue_cents** | **int** |  | 
**publisher_share_percent** | **int** |  | 
**publisher_earnings_cents** | **int** |  | 
**status** | **str** |  | 
**deal_count** | **int** |  | 

## Example

```python
from encypher.models.earnings_summary import EarningsSummary

# TODO update the JSON string below
json = "{}"
# create an instance of EarningsSummary from a JSON string
earnings_summary_instance = EarningsSummary.from_json(json)
# print the JSON string representation of the object
print(EarningsSummary.to_json())

# convert the object into a dict
earnings_summary_dict = earnings_summary_instance.to_dict()
# create an instance of EarningsSummary from a dict
earnings_summary_from_dict = EarningsSummary.from_dict(earnings_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


