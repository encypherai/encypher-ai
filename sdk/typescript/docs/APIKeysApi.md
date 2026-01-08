# APIKeysApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createKeyApiV1KeysPost**](APIKeysApi.md#createkeyapiv1keyspost) | **POST** /api/v1/keys | Create Key |
| [**createKeyApiV1KeysPost_0**](APIKeysApi.md#createkeyapiv1keyspost_0) | **POST** /api/v1/keys | Create Key |
| [**listKeysApiV1KeysGet**](APIKeysApi.md#listkeysapiv1keysget) | **GET** /api/v1/keys | List Keys |
| [**listKeysApiV1KeysGet_0**](APIKeysApi.md#listkeysapiv1keysget_0) | **GET** /api/v1/keys | List Keys |
| [**revokeKeyApiV1KeysKeyIdDelete**](APIKeysApi.md#revokekeyapiv1keyskeyiddelete) | **DELETE** /api/v1/keys/{key_id} | Revoke Key |
| [**revokeKeyApiV1KeysKeyIdDelete_0**](APIKeysApi.md#revokekeyapiv1keyskeyiddelete_0) | **DELETE** /api/v1/keys/{key_id} | Revoke Key |
| [**rotateKeyApiV1KeysKeyIdRotatePost**](APIKeysApi.md#rotatekeyapiv1keyskeyidrotatepost) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key |
| [**rotateKeyApiV1KeysKeyIdRotatePost_0**](APIKeysApi.md#rotatekeyapiv1keyskeyidrotatepost_0) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key |
| [**updateKeyApiV1KeysKeyIdPatch**](APIKeysApi.md#updatekeyapiv1keyskeyidpatch) | **PATCH** /api/v1/keys/{key_id} | Update Key |
| [**updateKeyApiV1KeysKeyIdPatch_0**](APIKeysApi.md#updatekeyapiv1keyskeyidpatch_0) | **PATCH** /api/v1/keys/{key_id} | Update Key |



## createKeyApiV1KeysPost

> KeyCreateResponse createKeyApiV1KeysPost(keyCreateRequest)

Create Key

Create a new API key.  The full key is only returned once - store it securely.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { CreateKeyApiV1KeysPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // KeyCreateRequest
    keyCreateRequest: ...,
  } satisfies CreateKeyApiV1KeysPostRequest;

  try {
    const data = await api.createKeyApiV1KeysPost(body);
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
| **keyCreateRequest** | [KeyCreateRequest](KeyCreateRequest.md) |  | |

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createKeyApiV1KeysPost_0

> KeyCreateResponse createKeyApiV1KeysPost_0(keyCreateRequest)

Create Key

Create a new API key.  The full key is only returned once - store it securely.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { CreateKeyApiV1KeysPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // KeyCreateRequest
    keyCreateRequest: ...,
  } satisfies CreateKeyApiV1KeysPost0Request;

  try {
    const data = await api.createKeyApiV1KeysPost_0(body);
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
| **keyCreateRequest** | [KeyCreateRequest](KeyCreateRequest.md) |  | |

### Return type

[**KeyCreateResponse**](KeyCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listKeysApiV1KeysGet

> KeyListResponse listKeysApiV1KeysGet(includeRevoked)

List Keys

List API keys for the organization.  Keys are masked - only the prefix is shown for security.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { ListKeysApiV1KeysGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // boolean | Include revoked keys (optional)
    includeRevoked: true,
  } satisfies ListKeysApiV1KeysGetRequest;

  try {
    const data = await api.listKeysApiV1KeysGet(body);
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
| **includeRevoked** | `boolean` | Include revoked keys | [Optional] [Defaults to `false`] |

### Return type

[**KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listKeysApiV1KeysGet_0

> KeyListResponse listKeysApiV1KeysGet_0(includeRevoked)

List Keys

List API keys for the organization.  Keys are masked - only the prefix is shown for security.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { ListKeysApiV1KeysGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // boolean | Include revoked keys (optional)
    includeRevoked: true,
  } satisfies ListKeysApiV1KeysGet0Request;

  try {
    const data = await api.listKeysApiV1KeysGet_0(body);
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
| **includeRevoked** | `boolean` | Include revoked keys | [Optional] [Defaults to `false`] |

### Return type

[**KeyListResponse**](KeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokeKeyApiV1KeysKeyIdDelete

> KeyRevokeResponse revokeKeyApiV1KeysKeyIdDelete(keyId)

Revoke Key

Revoke an API key.  The key will immediately stop working. This action cannot be undone.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { RevokeKeyApiV1KeysKeyIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
  } satisfies RevokeKeyApiV1KeysKeyIdDeleteRequest;

  try {
    const data = await api.revokeKeyApiV1KeysKeyIdDelete(body);
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

### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokeKeyApiV1KeysKeyIdDelete_0

> KeyRevokeResponse revokeKeyApiV1KeysKeyIdDelete_0(keyId)

Revoke Key

Revoke an API key.  The key will immediately stop working. This action cannot be undone.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { RevokeKeyApiV1KeysKeyIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
  } satisfies RevokeKeyApiV1KeysKeyIdDelete0Request;

  try {
    const data = await api.revokeKeyApiV1KeysKeyIdDelete_0(body);
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

### Return type

[**KeyRevokeResponse**](KeyRevokeResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rotateKeyApiV1KeysKeyIdRotatePost

> KeyRotateResponse rotateKeyApiV1KeysKeyIdRotatePost(keyId)

Rotate Key

Rotate an API key.  Creates a new key with the same permissions and revokes the old one. The new key is only returned once - store it securely.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { RotateKeyApiV1KeysKeyIdRotatePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
  } satisfies RotateKeyApiV1KeysKeyIdRotatePostRequest;

  try {
    const data = await api.rotateKeyApiV1KeysKeyIdRotatePost(body);
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

### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rotateKeyApiV1KeysKeyIdRotatePost_0

> KeyRotateResponse rotateKeyApiV1KeysKeyIdRotatePost_0(keyId)

Rotate Key

Rotate an API key.  Creates a new key with the same permissions and revokes the old one. The new key is only returned once - store it securely.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { RotateKeyApiV1KeysKeyIdRotatePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
  } satisfies RotateKeyApiV1KeysKeyIdRotatePost0Request;

  try {
    const data = await api.rotateKeyApiV1KeysKeyIdRotatePost_0(body);
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

### Return type

[**KeyRotateResponse**](KeyRotateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateKeyApiV1KeysKeyIdPatch

> KeyUpdateResponse updateKeyApiV1KeysKeyIdPatch(keyId, keyUpdateRequest)

Update Key

Update an API key\&#39;s name or permissions.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { UpdateKeyApiV1KeysKeyIdPatchRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
    // KeyUpdateRequest
    keyUpdateRequest: ...,
  } satisfies UpdateKeyApiV1KeysKeyIdPatchRequest;

  try {
    const data = await api.updateKeyApiV1KeysKeyIdPatch(body);
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
| **keyUpdateRequest** | [KeyUpdateRequest](KeyUpdateRequest.md) |  | |

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## updateKeyApiV1KeysKeyIdPatch_0

> KeyUpdateResponse updateKeyApiV1KeysKeyIdPatch_0(keyId, keyUpdateRequest)

Update Key

Update an API key\&#39;s name or permissions.

### Example

```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { UpdateKeyApiV1KeysKeyIdPatch0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // string
    keyId: keyId_example,
    // KeyUpdateRequest
    keyUpdateRequest: ...,
  } satisfies UpdateKeyApiV1KeysKeyIdPatch0Request;

  try {
    const data = await api.updateKeyApiV1KeysKeyIdPatch_0(body);
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
| **keyUpdateRequest** | [KeyUpdateRequest](KeyUpdateRequest.md) |  | |

### Return type

[**KeyUpdateResponse**](KeyUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

