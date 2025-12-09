# PayoutResponse

Schema for payout response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**distribution_id** | **str** |  | 
**total_members_paid** | **int** |  | 
**total_amount_paid** | **str** |  | 
**failed_payments** | **List[str]** |  | [optional] [default to []]

## Example

```python
from encypher.models.payout_response import PayoutResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PayoutResponse from a JSON string
payout_response_instance = PayoutResponse.from_json(json)
# print the JSON string representation of the object
print(PayoutResponse.to_json())

# convert the object into a dict
payout_response_dict = payout_response_instance.to_dict()
# create an instance of PayoutResponse from a dict
payout_response_from_dict = PayoutResponse.from_dict(payout_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


