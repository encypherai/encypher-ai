# PayoutCreate

Schema for processing payouts.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**distribution_id** | **str** |  | 
**payment_method** | **str** |  | [optional] [default to 'stripe']

## Example

```python
from encypher.models.payout_create import PayoutCreate

# TODO update the JSON string below
json = "{}"
# create an instance of PayoutCreate from a JSON string
payout_create_instance = PayoutCreate.from_json(json)
# print the JSON string representation of the object
print(PayoutCreate.to_json())

# convert the object into a dict
payout_create_dict = payout_create_instance.to_dict()
# create an instance of PayoutCreate from a dict
payout_create_from_dict = PayoutCreate.from_dict(payout_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


