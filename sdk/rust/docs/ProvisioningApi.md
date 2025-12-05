# \ProvisioningApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**auto_provision_api_v1_provisioning_auto_provision_post**](ProvisioningApi.md#auto_provision_api_v1_provisioning_auto_provision_post) | **POST** /api/v1/provisioning/auto-provision | Auto-provision Organization and API Key
[**create_api_key_api_v1_provisioning_api_keys_post**](ProvisioningApi.md#create_api_key_api_v1_provisioning_api_keys_post) | **POST** /api/v1/provisioning/api-keys | Create API Key
[**create_user_account_api_v1_provisioning_users_post**](ProvisioningApi.md#create_user_account_api_v1_provisioning_users_post) | **POST** /api/v1/provisioning/users | Create User Account
[**list_api_keys_api_v1_provisioning_api_keys_get**](ProvisioningApi.md#list_api_keys_api_v1_provisioning_api_keys_get) | **GET** /api/v1/provisioning/api-keys | List API Keys
[**provisioning_health_api_v1_provisioning_health_get**](ProvisioningApi.md#provisioning_health_api_v1_provisioning_health_get) | **GET** /api/v1/provisioning/health | Provisioning Service Health
[**revoke_api_key_api_v1_provisioning_api_keys_key_id_delete**](ProvisioningApi.md#revoke_api_key_api_v1_provisioning_api_keys_key_id_delete) | **DELETE** /api/v1/provisioning/api-keys/{key_id} | Revoke API Key



## auto_provision_api_v1_provisioning_auto_provision_post

> models::AutoProvisionResponse auto_provision_api_v1_provisioning_auto_provision_post(auto_provision_request, x_provisioning_token)
Auto-provision Organization and API Key

Automatically provision an organization, user account, and API key.          This endpoint is designed for external services to automatically create     accounts without manual intervention:          **Use Cases:**     - SDK initialization (auto-create account on first use)     - WordPress plugin activation (auto-provision on install)     - CLI tool setup (auto-create account on login)     - Mobile app onboarding (auto-provision on signup)          **What Gets Created:**     1. Organization (with specified tier)     2. User account (associated with email)     3. API key (for authentication)          **Idempotent:** If organization already exists for email, returns existing     organization with a new API key.          **Rate Limits:**     - 10 requests per minute per IP     - 100 requests per hour per email          **Security:**     - Requires valid provisioning token (for production)     - Validates email format     - Logs all provisioning events

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**auto_provision_request** | [**AutoProvisionRequest**](AutoProvisionRequest.md) |  | [required] |
**x_provisioning_token** | Option<**String**> | Provisioning token (optional) |  |

### Return type

[**models::AutoProvisionResponse**](AutoProvisionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_api_key_api_v1_provisioning_api_keys_post

> models::ApiKeyResponse create_api_key_api_v1_provisioning_api_keys_post(api_key_create_request)
Create API Key

Create a new API key for an organization

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**api_key_create_request** | [**ApiKeyCreateRequest**](ApiKeyCreateRequest.md) |  | [required] |

### Return type

[**models::ApiKeyResponse**](APIKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_user_account_api_v1_provisioning_users_post

> models::UserAccountResponse create_user_account_api_v1_provisioning_users_post(user_account_create_request)
Create User Account

Create a new user account

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**user_account_create_request** | [**UserAccountCreateRequest**](UserAccountCreateRequest.md) |  | [required] |

### Return type

[**models::UserAccountResponse**](UserAccountResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_api_keys_api_v1_provisioning_api_keys_get

> models::ApiKeyListResponse list_api_keys_api_v1_provisioning_api_keys_get()
List API Keys

List all API keys for an organization

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::ApiKeyListResponse**](APIKeyListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## provisioning_health_api_v1_provisioning_health_get

> serde_json::Value provisioning_health_api_v1_provisioning_health_get()
Provisioning Service Health

Check if provisioning service is available

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_api_key_api_v1_provisioning_api_keys_key_id_delete

> revoke_api_key_api_v1_provisioning_api_keys_key_id_delete(key_id, api_key_revoke_request)
Revoke API Key

Revoke an API key

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**api_key_revoke_request** | [**ApiKeyRevokeRequest**](ApiKeyRevokeRequest.md) |  | [required] |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

