# MerkleRootResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_id** | [**uuid::Uuid**](uuid::Uuid.md) | Unique identifier for the Merkle root | 
**document_id** | **String** | Document identifier | 
**root_hash** | **String** | SHA-256 hash of the Merkle tree root | 
**tree_depth** | **i32** | Height of the Merkle tree | 
**total_leaves** | **i32** | Number of leaf nodes in the tree | 
**segmentation_level** | **String** | Segmentation level (word/sentence/paragraph/section) | 
**created_at** | **String** | Timestamp when the root was created | 
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


