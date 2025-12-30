# TrustAnchorResponse

Response for trust anchor lookup.  Enables external C2PA validators to verify Encypher-signed content by providing the signer's public key.  See: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**signer_id** | **str** | The signer identifier | 
**signer_name** | **str** | Human-readable signer name | 
**public_key** | **str** | PEM-encoded public key | 
**public_key_algorithm** | **str** | Key algorithm | [optional] [default to 'Ed25519']
**key_id** | **str** |  | [optional] 
**issued_at** | **str** |  | [optional] 
**expires_at** | **str** |  | [optional] 
**revoked** | **bool** | Whether the key has been revoked | [optional] [default to False]
**trust_anchor_type** | **str** | Type of trust anchor | [optional] [default to 'organization']

## Example

```python
from encypher.models.trust_anchor_response import TrustAnchorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TrustAnchorResponse from a JSON string
trust_anchor_response_instance = TrustAnchorResponse.from_json(json)
# print the JSON string representation of the object
print(TrustAnchorResponse.to_json())

# convert the object into a dict
trust_anchor_response_dict = trust_anchor_response_instance.to_dict()
# create an instance of TrustAnchorResponse from a dict
trust_anchor_response_from_dict = TrustAnchorResponse.from_dict(trust_anchor_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


