# EncodeWithEmbeddingsResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | Option<**bool**> | Whether encoding succeeded | [optional][default to true]
**document_id** | **String** | Document identifier | 
**merkle_tree** | Option<[**models::MerkleTreeInfo**](MerkleTreeInfo.md)> |  | [optional]
**merkle_trees** | Option<[**std::collections::HashMap<String, models::MerkleTreeLevelInfo>**](MerkleTreeLevelInfo.md)> |  | [optional]
**embeddings** | [**Vec<models::EmbeddingInfo>**](EmbeddingInfo.md) | List of generated embeddings | 
**embedded_content** | Option<**String**> |  | [optional]
**statistics** | [**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md) | Processing statistics | 
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


