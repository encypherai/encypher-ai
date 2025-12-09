# BatchItemResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Document identifier from request | 
**status** | **String** | Processing outcome for the document | 
**signed_text** | Option<**String**> |  | [optional]
**embedded_content** | Option<**String**> |  | [optional]
**verdict** | Option<[**models::AppModelsResponseModelsVerifyVerdict**](app__models__response_models__VerifyVerdict.md)> |  | [optional]
**error_code** | Option<**String**> |  | [optional]
**error_message** | Option<**String**> |  | [optional]
**statistics** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> | Timing and segmentation statistics for the item | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


