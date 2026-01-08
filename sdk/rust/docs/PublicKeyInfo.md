# PublicKeyInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **String** | Key ID | 
**organization_id** | **String** | Organization that owns this key | 
**key_name** | Option<**String**> |  | [optional]
**key_algorithm** | **String** | Key algorithm | 
**key_fingerprint** | **String** | SHA-256 fingerprint of the public key | 
**public_key_pem** | **String** | PEM-encoded public key | 
**is_active** | Option<**bool**> | Whether key is active for verification | [optional][default to true]
**created_at** | **String** | When key was registered | 
**last_used_at** | Option<**String**> |  | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


