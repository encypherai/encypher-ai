# SourceRecord

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Source document ID | 
**organization_id** | **String** | Source organization ID | 
**organization_name** | Option<**String**> |  | [optional]
**segment_hash** | **String** | Hash of the matched segment | 
**leaf_index** | **i32** | Index in source Merkle tree | 
**merkle_root_hash** | Option<**String**> |  | [optional]
**created_at** | **String** | When content was first registered | 
**signed_at** | Option<**String**> |  | [optional]
**confidence** | **f64** | Match confidence (0-1) | 
**authority_score** | Option<**f64**> |  | [optional]
**is_original** | **bool** | Whether this is the original source | 
**previous_source_id** | Option<**String**> |  | [optional]
**next_source_id** | Option<**String**> |  | [optional]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


