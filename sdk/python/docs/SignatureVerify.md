# SignatureVerify

Schema for signature verification

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | **str** |  | 
**signature** | **str** |  | 
**public_key_pem** | **str** |  | 

## Example

```python
from encypher.models.signature_verify import SignatureVerify

# TODO update the JSON string below
json = "{}"
# create an instance of SignatureVerify from a JSON string
signature_verify_instance = SignatureVerify.from_json(json)
# print the JSON string representation of the object
print(SignatureVerify.to_json())

# convert the object into a dict
signature_verify_dict = signature_verify_instance.to_dict()
# create an instance of SignatureVerify from a dict
signature_verify_from_dict = SignatureVerify.from_dict(signature_verify_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


