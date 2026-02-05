# VerificationServiceVerifyVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  | 
**tampered** | **bool** |  | 
**reason_code** | **String** |  | 
**signer_id** | Option<**String**> |  | [optional]
**signer_name** | Option<**String**> |  | [optional]
**organization_id** | Option<**String**> |  | [optional]
**organization_name** | Option<**String**> |  | [optional]
**timestamp** | Option<**String**> |  | [optional]
**document** | Option<[**models::DocumentInfo**](DocumentInfo.md)> |  | [optional]
**c2pa** | Option<[**models::C2PaInfo**](C2PAInfo.md)> |  | [optional]
**licensing** | Option<[**models::LicensingInfo**](LicensingInfo.md)> |  | [optional]
**merkle_proof** | Option<[**models::MerkleProofInfo**](MerkleProofInfo.md)> |  | [optional]
**details** | Option<[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


