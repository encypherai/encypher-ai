# EvidenceGenerateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_text** | **String** | Text content to generate evidence for | 
**document_id** | Option<**String**> |  | [optional]
**include_merkle_proof** | Option<**bool**> | Include Merkle proof in evidence package | [optional][default to true]
**include_signature_chain** | Option<**bool**> | Include full signature verification chain | [optional][default to true]
**include_timestamp_proof** | Option<**bool**> | Include timestamp verification | [optional][default to true]
**export_format** | Option<**String**> | Export format: json, pdf, or both | [optional][default to json]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


