# VerificationStats

Schema for verification statistics

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_verifications** | **int** |  | 
**valid_verifications** | **int** |  | 
**invalid_verifications** | **int** |  | 
**tampered_documents** | **int** |  | 
**average_confidence_score** | **float** |  | 
**average_verification_time_ms** | **float** |  | 

## Example

```python
from encypher.models.verification_stats import VerificationStats

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationStats from a JSON string
verification_stats_instance = VerificationStats.from_json(json)
# print the JSON string representation of the object
print(VerificationStats.to_json())

# convert the object into a dict
verification_stats_dict = verification_stats_instance.to_dict()
# create an instance of VerificationStats from a dict
verification_stats_from_dict = VerificationStats.from_dict(verification_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


