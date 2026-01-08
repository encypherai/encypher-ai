# EncodeWithEmbeddingsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Unique document identifier | 
**text** | **String** | Full document text to encode | 
**segmentation_level** | Option<**String**> | Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word | [optional][default to sentence]
**action** | Option<**String**> | C2PA action type: c2pa.created (new content) or c2pa.edited (modified content) | [optional][default to c2pa.created]
**previous_instance_id** | Option<**String**> |  | [optional]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**c2pa_manifest_url** | Option<**String**> |  | [optional]
**c2pa_manifest_hash** | Option<**String**> |  | [optional]
**custom_assertions** | Option<[**Vec<std::collections::HashMap<String, serde_json::Value>>**](std::collections::HashMap.md)> |  | [optional]
**template_id** | Option<**String**> |  | [optional]
**validate_assertions** | Option<**bool**> | Whether to validate custom assertions against registered schemas | [optional][default to true]
**digital_source_type** | Option<**String**> |  | [optional]
**license** | Option<[**models::LicenseInfo**](LicenseInfo.md)> |  | [optional]
**rights** | Option<[**models::AppSchemasEmbeddingsRightsMetadata**](app__schemas__embeddings__RightsMetadata.md)> |  | [optional]
**embedding_options** | Option<[**models::EmbeddingOptions**](EmbeddingOptions.md)> | Embedding generation options | [optional]
**expires_at** | Option<**String**> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


