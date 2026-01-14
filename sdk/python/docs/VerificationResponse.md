# VerificationResponse

Schema for verification response

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_valid** | **bool** |  | 
**is_tampered** | **bool** |  | 
**signature_valid** | **bool** |  | 
**hash_valid** | **bool** |  | 
**confidence_score** | **float** |  | 
**similarity_score** | **float** |  | 
**signer_id** | **str** |  | 
**warnings** | **List[str]** |  | 
**verification_time_ms** | **int** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from encypher.models.verification_response import VerificationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationResponse from a JSON string
verification_response_instance = VerificationResponse.from_json(json)
# print the JSON string representation of the object
print(VerificationResponse.to_json())

# convert the object into a dict
verification_response_dict = verification_response_instance.to_dict()
# create an instance of VerificationResponse from a dict
verification_response_from_dict = VerificationResponse.from_dict(verification_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


