# PayoutSummary

Payout summary.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**period_start** | **str** |  | 
**period_end** | **str** |  | 
**total_earnings_cents** | **int** |  | 
**payout_amount_cents** | **int** |  | 
**currency** | **str** |  | 
**status** | **str** |  | 
**paid_at** | **str** |  | [optional] 

## Example

```python
from encypher.models.payout_summary import PayoutSummary

# TODO update the JSON string below
json = "{}"
# create an instance of PayoutSummary from a JSON string
payout_summary_instance = PayoutSummary.from_json(json)
# print the JSON string representation of the object
print(PayoutSummary.to_json())

# convert the object into a dict
payout_summary_dict = payout_summary_instance.to_dict()
# create an instance of PayoutSummary from a dict
payout_summary_from_dict = PayoutSummary.from_dict(payout_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


