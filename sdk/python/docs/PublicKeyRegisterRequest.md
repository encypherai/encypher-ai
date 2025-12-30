# PublicKeyRegisterRequest

Request to register a BYOK public key.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**public_key_pem** | **str** | PEM-encoded public key (Ed25519 or RSA) | 
**key_name** | **str** |  | [optional] 
**key_algorithm** | **str** | Key algorithm (Ed25519, RSA-2048, RSA-4096) | [optional] [default to 'Ed25519']

## Example

```python
from encypher.models.public_key_register_request import PublicKeyRegisterRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PublicKeyRegisterRequest from a JSON string
public_key_register_request_instance = PublicKeyRegisterRequest.from_json(json)
# print the JSON string representation of the object
print(PublicKeyRegisterRequest.to_json())

# convert the object into a dict
public_key_register_request_dict = public_key_register_request_instance.to_dict()
# create an instance of PublicKeyRegisterRequest from a dict
public_key_register_request_from_dict = PublicKeyRegisterRequest.from_dict(public_key_register_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


