# VerificationServiceVerifyVerdict

Core verification result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  | 
**tampered** | **bool** |  | 
**reason_code** | **str** |  | 
**signer_id** | **str** |  | [optional] 
**signer_name** | **str** |  | [optional] 
**organization_id** | **str** |  | [optional] 
**organization_name** | **str** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 
**document** | [**DocumentInfo**](DocumentInfo.md) |  | [optional] 
**c2pa** | [**C2PAInfo**](C2PAInfo.md) |  | [optional] 
**licensing** | [**LicensingInfo**](LicensingInfo.md) |  | [optional] 
**merkle_proof** | [**MerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**details** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.verification_service_verify_verdict import VerificationServiceVerifyVerdict

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceVerifyVerdict from a JSON string
verification_service_verify_verdict_instance = VerificationServiceVerifyVerdict.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceVerifyVerdict.to_json())

# convert the object into a dict
verification_service_verify_verdict_dict = verification_service_verify_verdict_instance.to_dict()
# create an instance of VerificationServiceVerifyVerdict from a dict
verification_service_verify_verdict_from_dict = VerificationServiceVerifyVerdict.from_dict(verification_service_verify_verdict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


