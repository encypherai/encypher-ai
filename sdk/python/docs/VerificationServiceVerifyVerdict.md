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
**publisher_name** | **str** |  | [optional]
**organization_id** | **str** |  | [optional]
**organization_name** | **str** |  | [optional]
**timestamp** | **datetime** |  | [optional]
**document** | [**VerificationServiceDocumentInfo**](VerificationServiceDocumentInfo.md) |  | [optional]
**c2pa** | [**VerificationServiceC2PAInfo**](VerificationServiceC2PAInfo.md) |  | [optional]
**licensing** | [**VerificationServiceLicensingInfo**](VerificationServiceLicensingInfo.md) |  | [optional]
**embeddings** | [**List[EmbeddingDetail]**](EmbeddingDetail.md) |  | [optional]
**total_embeddings** | **int** |  | [optional]
**total_segments_in_document** | **int** |  | [optional]
**merkle_proof** | [**VerificationServiceMerkleProofInfo**](VerificationServiceMerkleProofInfo.md) |  | [optional]
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
