# EmbeddingVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **i32** | Index of this embedding (0-based) | 
**valid** | **bool** | Whether the signature is valid | 
**tampered** | **bool** | Whether the payload was tampered | 
**reason_code** | **String** | Reason code describing the verdict | 
**signer_id** | Option<**String**> |  | [optional]
**signer_name** | Option<**String**> |  | [optional]
**timestamp** | Option<**String**> |  | [optional]
**text_span** | Option<[**Vec<serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**clean_text** | Option<**String**> |  | [optional]
**manifest** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


