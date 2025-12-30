# PublicKeyRegisterResponse

Response for public key registration.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**data** | [**PublicKeyInfo**](PublicKeyInfo.md) |  | [optional] 
**error** | **str** |  | [optional] 

## Example

```python
from encypher.models.public_key_register_response import PublicKeyRegisterResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PublicKeyRegisterResponse from a JSON string
public_key_register_response_instance = PublicKeyRegisterResponse.from_json(json)
# print the JSON string representation of the object
print(PublicKeyRegisterResponse.to_json())

# convert the object into a dict
public_key_register_response_dict = public_key_register_response_instance.to_dict()
# create an instance of PublicKeyRegisterResponse from a dict
public_key_register_response_from_dict = PublicKeyRegisterResponse.from_dict(public_key_register_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


