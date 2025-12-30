# \ByokApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_public_keys_api_v1_byok_public_keys_get**](ByokApi.md#list_public_keys_api_v1_byok_public_keys_get) | **GET** /api/v1/byok/public-keys | List public keys
[**list_public_keys_api_v1_byok_public_keys_get_0**](ByokApi.md#list_public_keys_api_v1_byok_public_keys_get_0) | **GET** /api/v1/byok/public-keys | List public keys
[**register_public_key_api_v1_byok_public_keys_post**](ByokApi.md#register_public_key_api_v1_byok_public_keys_post) | **POST** /api/v1/byok/public-keys | Register a public key
[**register_public_key_api_v1_byok_public_keys_post_0**](ByokApi.md#register_public_key_api_v1_byok_public_keys_post_0) | **POST** /api/v1/byok/public-keys | Register a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete**](ByokApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete_0**](ByokApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete_0) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key



## list_public_keys_api_v1_byok_public_keys_get

> models::PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get(include_revoked)
List public keys

List all registered public keys for the organization.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_public_keys_api_v1_byok_public_keys_get_0

> models::PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get_0(include_revoked)
List public keys

List all registered public keys for the organization.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## register_public_key_api_v1_byok_public_keys_post

> models::PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post(public_key_register_request)
Register a public key

Register a BYOK public key for signature verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | [required] |

### Return type

[**models::PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## register_public_key_api_v1_byok_public_keys_post_0

> models::PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post_0(public_key_register_request)
Register a public key

Register a BYOK public key for signature verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | [required] |

### Return type

[**models::PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_public_key_api_v1_byok_public_keys_key_id_delete

> std::collections::HashMap<String, serde_json::Value> revoke_public_key_api_v1_byok_public_keys_key_id_delete(key_id, reason)
Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**reason** | Option<**String**> | Reason for revocation |  |

### Return type

[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_public_key_api_v1_byok_public_keys_key_id_delete_0

> std::collections::HashMap<String, serde_json::Value> revoke_public_key_api_v1_byok_public_keys_key_id_delete_0(key_id, reason)
Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**reason** | Option<**String**> | Reason for revocation |  |

### Return type

[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

