# ProvisioningApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**autoProvisionApiV1ProvisioningAutoProvisionPost**](ProvisioningApi.md#autoprovisionapiv1provisioningautoprovisionpost) | **POST** /api/v1/provisioning/auto-provision | Auto-provision Organization and API Key |
| [**createApiKeyApiV1ProvisioningApiKeysPost**](ProvisioningApi.md#createapikeyapiv1provisioningapikeyspost) | **POST** /api/v1/provisioning/api-keys | Create API Key |
| [**createUserAccountApiV1ProvisioningUsersPost**](ProvisioningApi.md#createuseraccountapiv1provisioninguserspost) | **POST** /api/v1/provisioning/users | Create User Account |
| [**listApiKeysApiV1ProvisioningApiKeysGet**](ProvisioningApi.md#listapikeysapiv1provisioningapikeysget) | **GET** /api/v1/provisioning/api-keys | List API Keys |
| [**provisioningHealthApiV1ProvisioningHealthGet**](ProvisioningApi.md#provisioninghealthapiv1provisioninghealthget) | **GET** /api/v1/provisioning/health | Provisioning Service Health |
| [**revokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete**](ProvisioningApi.md#revokeapikeyapiv1provisioningapikeyskeyiddelete) | **DELETE** /api/v1/provisioning/api-keys/{key_id} | Revoke API Key |



## autoProvisionApiV1ProvisioningAutoProvisionPost

> AutoProvisionResponse autoProvisionApiV1ProvisioningAutoProvisionPost(autoProvisionRequest, xProvisioningToken)

Auto-provision Organization and API Key

Automatically provision an organization, user account, and API key.          This endpoint is designed for external services to automatically create     accounts without manual intervention:          **Use Cases:**     - SDK initialization (auto-create account on first use)     - WordPress plugin activation (auto-provision on install)     - CLI tool setup (auto-create account on login)     - Mobile app onboarding (auto-provision on signup)          **What Gets Created:**     1. Organization (with specified tier)     2. User account (associated with email)     3. API key (for authentication)          **Idempotent:** If organization already exists for email, returns existing     organization with a new API key.          **Rate Limits:**     - 10 requests per minute per IP     - 100 requests per hour per email          **Security:**     - Requires valid provisioning token (for production)     - Validates email format     - Logs all provisioning events

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { AutoProvisionApiV1ProvisioningAutoProvisionPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  const body = {
    // AutoProvisionRequest
    autoProvisionRequest: ...,
    // string | Provisioning token (optional) (optional)
    xProvisioningToken: xProvisioningToken_example,
  } satisfies AutoProvisionApiV1ProvisioningAutoProvisionPostRequest;

  try {
    const data = await api.autoProvisionApiV1ProvisioningAutoProvisionPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **autoProvisionRequest** | [AutoProvisionRequest](AutoProvisionRequest.md) |  | |
| **xProvisioningToken** | `string` | Provisioning token (optional) | [Optional] [Defaults to `undefined`] |

### Return type

[**AutoProvisionResponse**](AutoProvisionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Organization and API key created successfully |  -  |
| **400** | Invalid request |  -  |
| **429** | Rate limit exceeded |  -  |
| **500** | Server error |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createApiKeyApiV1ProvisioningApiKeysPost

> APIKeyResponse createApiKeyApiV1ProvisioningApiKeysPost(aPIKeyCreateRequest)

Create API Key

Create a new API key for an organization

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { CreateApiKeyApiV1ProvisioningApiKeysPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  const body = {
    // APIKeyCreateRequest
    aPIKeyCreateRequest: ...,
  } satisfies CreateApiKeyApiV1ProvisioningApiKeysPostRequest;

  try {
    const data = await api.createApiKeyApiV1ProvisioningApiKeysPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **aPIKeyCreateRequest** | [APIKeyCreateRequest](APIKeyCreateRequest.md) |  | |

### Return type

[**APIKeyResponse**](APIKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createUserAccountApiV1ProvisioningUsersPost

> UserAccountResponse createUserAccountApiV1ProvisioningUsersPost(userAccountCreateRequest)

Create User Account

Create a new user account

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { CreateUserAccountApiV1ProvisioningUsersPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  const body = {
    // UserAccountCreateRequest
    userAccountCreateRequest: ...,
  } satisfies CreateUserAccountApiV1ProvisioningUsersPostRequest;

  try {
    const data = await api.createUserAccountApiV1ProvisioningUsersPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userAccountCreateRequest** | [UserAccountCreateRequest](UserAccountCreateRequest.md) |  | |

### Return type

[**UserAccountResponse**](UserAccountResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listApiKeysApiV1ProvisioningApiKeysGet

> APIKeyListResponse listApiKeysApiV1ProvisioningApiKeysGet()

List API Keys

List all API keys for an organization

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { ListApiKeysApiV1ProvisioningApiKeysGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  try {
    const data = await api.listApiKeysApiV1ProvisioningApiKeysGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**APIKeyListResponse**](APIKeyListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## provisioningHealthApiV1ProvisioningHealthGet

> any provisioningHealthApiV1ProvisioningHealthGet()

Provisioning Service Health

Check if provisioning service is available

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { ProvisioningHealthApiV1ProvisioningHealthGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  try {
    const data = await api.provisioningHealthApiV1ProvisioningHealthGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete

> revokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete(keyId, aPIKeyRevokeRequest)

Revoke API Key

Revoke an API key

### Example

```ts
import {
  Configuration,
  ProvisioningApi,
} from '@encypher/sdk';
import type { RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new ProvisioningApi();

  const body = {
    // string
    keyId: keyId_example,
    // APIKeyRevokeRequest
    aPIKeyRevokeRequest: ...,
  } satisfies RevokeApiKeyApiV1ProvisioningApiKeysKeyIdDeleteRequest;

  try {
    const data = await api.revokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **keyId** | `string` |  | [Defaults to `undefined`] |
| **aPIKeyRevokeRequest** | [APIKeyRevokeRequest](APIKeyRevokeRequest.md) |  | |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

