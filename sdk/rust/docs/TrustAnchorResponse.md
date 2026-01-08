# TrustAnchorResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**signer_id** | **String** | The signer identifier | 
**signer_name** | **String** | Human-readable signer name | 
**public_key** | **String** | PEM-encoded public key | 
**public_key_algorithm** | Option<**String**> | Key algorithm | [optional][default to Ed25519]
**key_id** | Option<**String**> |  | [optional]
**issued_at** | Option<**String**> |  | [optional]
**expires_at** | Option<**String**> |  | [optional]
**revoked** | Option<**bool**> | Whether the key has been revoked | [optional][default to false]
**trust_anchor_type** | Option<**String**> | Type of trust anchor | [optional][default to organization]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


