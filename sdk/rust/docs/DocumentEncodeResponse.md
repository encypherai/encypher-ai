# DocumentEncodeResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether encoding was successful | 
**message** | **String** | Success or error message | 
**document_id** | **String** | Document identifier | 
**organization_id** | **String** | Organization identifier | 
**roots** | [**std::collections::HashMap<String, models::MerkleRootResponse>**](MerkleRootResponse.md) | Dictionary mapping segmentation level to Merkle root | 
**total_segments** | **std::collections::HashMap<String, i32>** | Number of segments at each level | 
**processing_time_ms** | **f64** | Processing time in milliseconds | 
**fuzzy_index** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


