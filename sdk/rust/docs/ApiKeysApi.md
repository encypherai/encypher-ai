# \ApiKeysApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_key_api_v1_keys_post**](ApiKeysApi.md#create_key_api_v1_keys_post) | **POST** /api/v1/keys | Create Key
[**create_key_api_v1_keys_post_0**](ApiKeysApi.md#create_key_api_v1_keys_post_0) | **POST** /api/v1/keys | Create Key
[**list_keys_api_v1_keys_get**](ApiKeysApi.md#list_keys_api_v1_keys_get) | **GET** /api/v1/keys | List Keys
[**list_keys_api_v1_keys_get_0**](ApiKeysApi.md#list_keys_api_v1_keys_get_0) | **GET** /api/v1/keys | List Keys
[**revoke_key_api_v1_keys_key_id_delete**](ApiKeysApi.md#revoke_key_api_v1_keys_key_id_delete) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
[**revoke_key_api_v1_keys_key_id_delete_0**](ApiKeysApi.md#revoke_key_api_v1_keys_key_id_delete_0) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
[**rotate_key_api_v1_keys_key_id_rotate_post**](ApiKeysApi.md#rotate_key_api_v1_keys_key_id_rotate_post) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
[**rotate_key_api_v1_keys_key_id_rotate_post_0**](ApiKeysApi.md#rotate_key_api_v1_keys_key_id_rotate_post_0) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
[**update_key_api_v1_keys_key_id_patch**](ApiKeysApi.md#update_key_api_v1_keys_key_id_patch) | **PATCH** /api/v1/keys/{key_id} | Update Key
[**update_key_api_v1_keys_key_id_patch_0**](ApiKeysApi.md#update_key_api_v1_keys_key_id_patch_0) | **PATCH** /api/v1/keys/{key_id} | Update Key



## create_key_api_v1_keys_post

> models::KeyCreateResponse create_key_api_v1_keys_post(key_create_request)
Create Key

Create a new API key.  The full key is only returned once - store it securely.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_create_request** | [**KeyCreateRequest**](KeyCreateRequest.md) |  | [required] |

### Return type

[**models::KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_key_api_v1_keys_post_0

> models::KeyCreateResponse create_key_api_v1_keys_post_0(key_create_request)
Create Key

Create a new API key.  The full key is only returned once - store it securely.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_create_request** | [**KeyCreateRequest**](KeyCreateRequest.md) |  | [required] |

### Return type

[**models::KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_keys_api_v1_keys_get

> models::KeyListResponse list_keys_api_v1_keys_get(include_revoked)
List Keys

List API keys for the organization.  Keys are masked - only the prefix is shown for security.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_keys_api_v1_keys_get_0

> models::KeyListResponse list_keys_api_v1_keys_get_0(include_revoked)
List Keys

List API keys for the organization.  Keys are masked - only the prefix is shown for security.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_key_api_v1_keys_key_id_delete

> models::KeyRevokeResponse revoke_key_api_v1_keys_key_id_delete(key_id)
Revoke Key

Revoke an API key.  The key will immediately stop working. This action cannot be undone.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |

### Return type

[**models::KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_key_api_v1_keys_key_id_delete_0

> models::KeyRevokeResponse revoke_key_api_v1_keys_key_id_delete_0(key_id)
Revoke Key

Revoke an API key.  The key will immediately stop working. This action cannot be undone.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |

### Return type

[**models::KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## rotate_key_api_v1_keys_key_id_rotate_post

> models::KeyRotateResponse rotate_key_api_v1_keys_key_id_rotate_post(key_id)
Rotate Key

Rotate an API key.  Creates a new key with the same permissions and revokes the old one. The new key is only returned once - store it securely.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |

### Return type

[**models::KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## rotate_key_api_v1_keys_key_id_rotate_post_0

> models::KeyRotateResponse rotate_key_api_v1_keys_key_id_rotate_post_0(key_id)
Rotate Key

Rotate an API key.  Creates a new key with the same permissions and revokes the old one. The new key is only returned once - store it securely.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |

### Return type

[**models::KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_key_api_v1_keys_key_id_patch

> models::KeyUpdateResponse update_key_api_v1_keys_key_id_patch(key_id, key_update_request)
Update Key

Update an API key's name or permissions.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**key_update_request** | [**KeyUpdateRequest**](KeyUpdateRequest.md) |  | [required] |

### Return type

[**models::KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_key_api_v1_keys_key_id_patch_0

> models::KeyUpdateResponse update_key_api_v1_keys_key_id_patch_0(key_id, key_update_request)
Update Key

Update an API key's name or permissions.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**key_update_request** | [**KeyUpdateRequest**](KeyUpdateRequest.md) |  | [required] |

### Return type

[**models::KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
