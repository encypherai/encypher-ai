# VerificationHistory

Schema for verification history

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**document_id** | **str** |  | 
**is_valid** | **bool** |  | 
**is_tampered** | **bool** |  | 
**confidence_score** | **float** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from encypher.models.verification_history import VerificationHistory

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationHistory from a JSON string
verification_history_instance = VerificationHistory.from_json(json)
# print the JSON string representation of the object
print(VerificationHistory.to_json())

# convert the object into a dict
verification_history_dict = verification_history_instance.to_dict()
# create an instance of VerificationHistory from a dict
verification_history_from_dict = VerificationHistory.from_dict(verification_history_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


