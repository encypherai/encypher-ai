# FingerprintEncodeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **String** | Unique document identifier | 
**text** | **String** | Text to fingerprint | 
**fingerprint_density** | Option<**f64**> | Density of fingerprint markers (0.01-0.5) | [optional][default to 0.1]
**fingerprint_key** | Option<**String**> |  | [optional]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


