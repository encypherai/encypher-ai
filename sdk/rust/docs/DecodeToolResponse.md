# DecodeToolResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**verification_status** | Option<**String**> |  | [optional][default to NotAttempted]
**error** | Option<**String**> |  | [optional]
**raw_hidden_data** | Option<[**models::AppRoutersToolsVerifyVerdict**](app__routers__tools__VerifyVerdict.md)> |  | [optional]
**embeddings_found** | Option<**i32**> | Number of embeddings found in the text | [optional][default to 0]
**all_embeddings** | Option<[**Vec<models::EmbeddingResult>**](EmbeddingResult.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


