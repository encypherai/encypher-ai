# EncodeWithEmbeddingsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Unique document identifier | 
**text** | **String** | Full document text to encode | 
**segmentation_level** | Option<**String**> | Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word | [optional][default to sentence]
**segmentation_levels** | Option<**Vec<String>**> |  | [optional]
**index_for_attribution** | Option<**bool**> |  | [optional]
**action** | Option<**String**> | C2PA action type: c2pa.created (new content) or c2pa.edited (modified content) | [optional][default to c2pa.created]
**manifest_mode** | Option<**String**> | Controls manifest detail level. Options: full, lightweight_uuid, hybrid. Availability depends on plan tier. | [optional][default to full]
**embedding_strategy** | Option<**String**> | Controls embedding placement strategy. Options: single_point, distributed, distributed_redundant. Availability depends on plan tier. | [optional][default to single_point]
**distribution_target** | Option<**String**> |  | [optional]
**add_dual_binding** | Option<**bool**> | Enable additional integrity binding. Availability depends on plan tier. | [optional][default to false]
**disable_c2pa** | Option<**bool**> | Opt-out of C2PA embedding. When true, only basic metadata is embedded. | [optional][default to false]
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


