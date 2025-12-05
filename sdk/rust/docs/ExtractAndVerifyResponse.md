# ExtractAndVerifyResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** | Whether embedding is valid | 
**verified_at** | Option<**String**> |  | [optional]
**content** | Option<[**models::ContentInfo**](ContentInfo.md)> |  | [optional]
**document** | Option<[**models::DocumentInfo**](DocumentInfo.md)> |  | [optional]
**merkle_proof** | Option<[**models::MerkleProofInfo**](MerkleProofInfo.md)> |  | [optional]
**c2pa** | Option<[**models::C2PaInfo**](C2PAInfo.md)> |  | [optional]
**licensing** | Option<[**models::LicensingInfo**](LicensingInfo.md)> |  | [optional]
**metadata** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]
**error** | Option<**String**> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


