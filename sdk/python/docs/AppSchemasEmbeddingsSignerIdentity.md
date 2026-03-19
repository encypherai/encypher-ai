# AppSchemasEmbeddingsSignerIdentity

Signer identity and trust chain information.  TEAM_165: When an org starts with a self-signed key managed by Encypher, micro markers are already cryptographically bound to that key. If the org later obtains a CA-signed certificate (via /byok/certificates), the trust chain upgrades automatically — no re-signing needed.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_id** | **str** | Organization identifier |
**organization_name** | **str** |  | [optional]
**certificate_status** | **str** | Certificate lifecycle: none, pending, active, expired, revoked |
**ca_backed** | **bool** | True if the org certificate chains to a trusted CA (not self-signed) | [optional] [default to False]
**issuer** | **str** |  | [optional]
**certificate_expiry** | **datetime** |  | [optional]
**trust_level** | **str** | Trust level: &#39;ca_verified&#39; (chains to C2PA-trusted CA), &#39;self_signed&#39; (Encypher-managed key), &#39;none&#39; (no certificate) | [optional] [default to 'self_signed']

## Example

```python
from encypher.models.app_schemas_embeddings_signer_identity import AppSchemasEmbeddingsSignerIdentity

# TODO update the JSON string below
json = "{}"
# create an instance of AppSchemasEmbeddingsSignerIdentity from a JSON string
app_schemas_embeddings_signer_identity_instance = AppSchemasEmbeddingsSignerIdentity.from_json(json)
# print the JSON string representation of the object
print(AppSchemasEmbeddingsSignerIdentity.to_json())

# convert the object into a dict
app_schemas_embeddings_signer_identity_dict = app_schemas_embeddings_signer_identity_instance.to_dict()
# create an instance of AppSchemasEmbeddingsSignerIdentity from a dict
app_schemas_embeddings_signer_identity_from_dict = AppSchemasEmbeddingsSignerIdentity.from_dict(app_schemas_embeddings_signer_identity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
