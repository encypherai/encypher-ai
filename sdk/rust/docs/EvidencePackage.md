# EvidencePackage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**evidence_id** | [**uuid::Uuid**](uuid::Uuid.md) | Unique evidence package ID | 
**generated_at** | **String** | When evidence was generated | 
**target_text_hash** | **String** | Hash of target text | 
**target_text_preview** | **String** | Preview of target text (first 200 chars) | 
**attribution_found** | **bool** | Whether attribution was found | 
**attribution_confidence** | **f64** | Overall confidence score | 
**source_document_id** | Option<**String**> |  | [optional]
**source_organization_id** | Option<**String**> |  | [optional]
**source_organization_name** | Option<**String**> |  | [optional]
**merkle_root_hash** | Option<**String**> |  | [optional]
**merkle_proof** | Option<[**Vec<models::MerkleProofItem>**](MerkleProofItem.md)> |  | [optional]
**merkle_proof_valid** | Option<**bool**> |  | [optional]
**signature_verification** | Option<[**models::SignatureVerification**](SignatureVerification.md)> |  | [optional]
**content_matches** | Option<[**Vec<models::ContentMatch>**](ContentMatch.md)> | List of matched content segments | [optional]
**original_timestamp** | Option<**String**> |  | [optional]
**timestamp_verified** | Option<**bool**> |  | [optional]
**json_export_url** | Option<**String**> |  | [optional]
**pdf_export_url** | Option<**String**> |  | [optional]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


