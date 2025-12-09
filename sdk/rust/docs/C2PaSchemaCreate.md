# C2PaSchemaCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | Human-readable name for the schema | 
**label** | **String** | Full assertion label (e.g., 'com.acme.legal.v1') | 
**version** | Option<**String**> | Schema version (e.g., 'v1', '1.0.0') | [optional][default to 1.0]
**json_schema** | [**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md) | JSON Schema for validation | 
**description** | Option<**String**> |  | [optional]
**is_public** | Option<**bool**> | Whether schema is publicly accessible | [optional][default to false]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


