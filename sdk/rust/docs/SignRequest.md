# SignRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **String** | Content to sign | 
**document_id** | Option<**String**> |  | [optional]
**document_title** | Option<**String**> |  | [optional]
**document_url** | Option<**String**> |  | [optional]
**document_type** | Option<**String**> | Document type: article | legal_brief | contract | ai_output | [optional][default to article]
**claim_generator** | Option<**String**> |  | [optional]
**actions** | Option<[**Vec<std::collections::HashMap<String, serde_json::Value>>**](std::collections::HashMap.md)> |  | [optional]
**template_id** | Option<**String**> |  | [optional]
**validate_assertions** | Option<**bool**> | Whether to validate template-based assertions (Business+). | [optional][default to true]
**rights** | Option<[**models::AppModelsRequestModelsRightsMetadata**](app__models__request_models__RightsMetadata.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


