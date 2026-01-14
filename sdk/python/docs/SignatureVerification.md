# SignatureVerification

Signature verification details.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**signer_id** | **str** | Signer identifier | 
**signer_name** | **str** |  | [optional] 
**algorithm** | **str** | Signature algorithm used | 
**public_key_fingerprint** | **str** | Public key fingerprint | 
**signature_valid** | **bool** | Whether signature is valid | 
**signed_at** | **datetime** |  | [optional] 

## Example

```python
from encypher.models.signature_verification import SignatureVerification

# TODO update the JSON string below
json = "{}"
# create an instance of SignatureVerification from a JSON string
signature_verification_instance = SignatureVerification.from_json(json)
# print the JSON string representation of the object
print(SignatureVerification.to_json())

# convert the object into a dict
signature_verification_dict = signature_verification_instance.to_dict()
# create an instance of SignatureVerification from a dict
signature_verification_from_dict = SignatureVerification.from_dict(signature_verification_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


