# EvidencePackage

Complete evidence package for content attribution.  This package contains all cryptographic proofs needed to verify content provenance in legal or compliance contexts.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evidence_id** | **str** | Unique evidence package ID | 
**generated_at** | **datetime** | When evidence was generated | 
**target_text_hash** | **str** | Hash of target text | 
**target_text_preview** | **str** | Preview of target text (first 200 chars) | 
**attribution_found** | **bool** | Whether attribution was found | 
**attribution_confidence** | **float** | Overall confidence score | 
**source_document_id** | **str** |  | [optional] 
**source_organization_id** | **str** |  | [optional] 
**source_organization_name** | **str** |  | [optional] 
**merkle_root_hash** | **str** |  | [optional] 
**merkle_proof** | [**List[MerkleProofItem]**](MerkleProofItem.md) |  | [optional] 
**merkle_proof_valid** | **bool** |  | [optional] 
**signature_verification** | [**SignatureVerification**](SignatureVerification.md) |  | [optional] 
**content_matches** | [**List[ContentMatch]**](ContentMatch.md) | List of matched content segments | [optional] 
**original_timestamp** | **datetime** |  | [optional] 
**timestamp_verified** | **bool** |  | [optional] 
**json_export_url** | **str** |  | [optional] 
**pdf_export_url** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.evidence_package import EvidencePackage

# TODO update the JSON string below
json = "{}"
# create an instance of EvidencePackage from a JSON string
evidence_package_instance = EvidencePackage.from_json(json)
# print the JSON string representation of the object
print(EvidencePackage.to_json())

# convert the object into a dict
evidence_package_dict = evidence_package_instance.to_dict()
# create an instance of EvidencePackage from a dict
evidence_package_from_dict = EvidencePackage.from_dict(evidence_package_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


