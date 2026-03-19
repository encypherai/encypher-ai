# SignerIdentity


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** |  | [optional]
**organization_name** | **str** |  | [optional]
**trust_level** | **str** |  | [optional] [default to 'unknown']

## Example

```python
from encypher.models.signer_identity import SignerIdentity

# TODO update the JSON string below
json = "{}"
# create an instance of SignerIdentity from a JSON string
signer_identity_instance = SignerIdentity.from_json(json)
# print the JSON string representation of the object
print(SignerIdentity.to_json())

# convert the object into a dict
signer_identity_dict = signer_identity_instance.to_dict()
# create an instance of SignerIdentity from a dict
signer_identity_from_dict = SignerIdentity.from_dict(signer_identity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
