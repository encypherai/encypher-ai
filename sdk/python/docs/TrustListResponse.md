# TrustListResponse

Response listing trusted CAs.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** |  | [optional] [default to True]
**trusted_cas** | **List[str]** |  | [optional]
**trust_list_url** | **str** |  | [optional] [default to 'https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem']
**trust_list_fingerprint** | **str** |  | [optional]
**trust_list_loaded_at** | **str** |  | [optional]
**trust_list_source** | **str** |  | [optional]
**trust_list_count** | **str** |  | [optional]
**required_signer_eku_oids** | **List[str]** |  | [optional]
**revocation_denylist** | **Dict[str, str]** |  | [optional]
**tsa_trust_list** | [**Dict[str, TsaTrustListValue]**](TsaTrustListValue.md) |  | [optional]
**default_signing_mode** | **str** |  | [optional] [default to 'organization']
**managed_signer_id** | **str** |  | [optional] [default to 'encypher_managed']

## Example

```python
from encypher.models.trust_list_response import TrustListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TrustListResponse from a JSON string
trust_list_response_instance = TrustListResponse.from_json(json)
# print the JSON string representation of the object
print(TrustListResponse.to_json())

# convert the object into a dict
trust_list_response_dict = trust_list_response_instance.to_dict()
# create an instance of TrustListResponse from a dict
trust_list_response_from_dict = TrustListResponse.from_dict(trust_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
