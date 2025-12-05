# AutoProvisionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether provisioning was successful | 
**message** | **String** | Success or error message | 
**organization_id** | **String** | Created organization ID | 
**organization_name** | **String** | Organization name | 
**user_id** | Option<**String**> |  | [optional]
**api_key** | [**models::ApiKeyResponse**](APIKeyResponse.md) | Generated API key | 
**tier** | **String** | Organization tier | 
**features_enabled** | **std::collections::HashMap<String, bool>** | Enabled features | 
**quota_limits** | **std::collections::HashMap<String, i32>** | Quota limits | 
**next_steps** | **std::collections::HashMap<String, String>** | Next steps and documentation links | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


