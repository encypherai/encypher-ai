# SignOptions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_type** | Option<**String**> | Document type: article, legal_brief, contract, ai_output | [optional][default to article]
**claim_generator** | Option<**String**> |  | [optional]
**action** | Option<**String**> | C2PA action type: c2pa.created (new) or c2pa.edited (modified) | [optional][default to c2pa.created]
**previous_instance_id** | Option<**String**> |  | [optional]
**digital_source_type** | Option<**String**> |  | [optional]
**segmentation_level** | Option<**String**> | Segmentation level: document (free), sentence, paragraph, section (Professional+), word (Enterprise) | [optional][default to document]
**segmentation_levels** | Option<**Vec<String>**> |  | [optional]
**manifest_mode** | Option<**String**> | Manifest mode: full (free), lightweight_uuid, minimal_uuid, hybrid, zw_embedding (Professional+) | [optional][default to full]
**embedding_strategy** | Option<**String**> | Embedding strategy: single_point (free), distributed, distributed_redundant (Professional+) | [optional][default to single_point]
**distribution_target** | Option<**String**> |  | [optional]
**index_for_attribution** | Option<**bool**> | Index content for attribution/plagiarism detection (Professional+) | [optional][default to false]
**custom_assertions** | Option<[**Vec<std::collections::HashMap<String, serde_json::Value>>**](std::collections::HashMap.md)> |  | [optional]
**template_id** | Option<**String**> |  | [optional]
**validate_assertions** | Option<**bool**> | Whether to validate custom assertions against registered schemas (Business+) | [optional][default to true]
**rights** | Option<[**models::RightsMetadata**](RightsMetadata.md)> |  | [optional]
**license** | Option<[**models::LicenseInfo**](LicenseInfo.md)> |  | [optional]
**actions** | Option<[**Vec<std::collections::HashMap<String, serde_json::Value>>**](std::collections::HashMap.md)> |  | [optional]
**add_dual_binding** | Option<**bool**> | Enable additional integrity binding (Enterprise) | [optional][default to false]
**include_fingerprint** | Option<**bool**> | Include robust fingerprint that survives modifications (Enterprise) | [optional][default to false]
**disable_c2pa** | Option<**bool**> | Opt-out of C2PA embedding, only basic metadata (Enterprise) | [optional][default to false]
**embedding_options** | Option<[**models::EmbeddingOptions**](EmbeddingOptions.md)> | Embedding output format options | [optional]
**expires_at** | Option<**String**> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


