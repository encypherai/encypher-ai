# DocumentEncodeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Unique identifier for the document | 
**text** | **String** | Document text content to encode | 
**segmentation_levels** | Option<**Vec<String>**> | Segmentation levels to encode (word/sentence/paragraph/section) | [optional][default to [sentence]]
**include_words** | Option<**bool**> | Whether to include word-level segmentation | [optional][default to false]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**fuzzy_fingerprint** | Option<[**models::FuzzyFingerprintConfig**](FuzzyFingerprintConfig.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


