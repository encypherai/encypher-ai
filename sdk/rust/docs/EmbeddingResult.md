# EmbeddingResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **i32** | Index of this embedding (0-based) | 
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**verification_status** | Option<**String**> |  | [optional][default to NotAttempted]
**error** | Option<**String**> |  | [optional]
**verdict** | Option<[**models::AppRoutersToolsVerifyVerdict**](app__routers__tools__VerifyVerdict.md)> |  | [optional]
**text_span** | Option<[**Vec<serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**clean_text** | Option<**String**> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


