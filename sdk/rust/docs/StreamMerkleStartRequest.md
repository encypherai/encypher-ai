# StreamMerkleStartRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Unique document identifier | 
**segmentation_level** | Option<**String**> | Segmentation level: sentence, paragraph, section | [optional][default to sentence]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**buffer_size** | Option<**i32**> | Maximum number of segments to buffer before forcing a flush | [optional][default to 100]
**auto_finalize_timeout_seconds** | Option<**i32**> | Timeout in seconds after which session auto-finalizes if idle | [optional][default to 300]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


