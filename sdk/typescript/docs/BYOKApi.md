# BYOKApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listPublicKeysApiV1ByokPublicKeysGet**](BYOKApi.md#listpublickeysapiv1byokpublickeysget) | **GET** /api/v1/byok/public-keys | List public keys |
| [**listPublicKeysApiV1ByokPublicKeysGet_0**](BYOKApi.md#listpublickeysapiv1byokpublickeysget_0) | **GET** /api/v1/byok/public-keys | List public keys |
| [**registerPublicKeyApiV1ByokPublicKeysPost**](BYOKApi.md#registerpublickeyapiv1byokpublickeyspost) | **POST** /api/v1/byok/public-keys | Register a public key |
| [**registerPublicKeyApiV1ByokPublicKeysPost_0**](BYOKApi.md#registerpublickeyapiv1byokpublickeyspost_0) | **POST** /api/v1/byok/public-keys | Register a public key |
| [**revokePublicKeyApiV1ByokPublicKeysKeyIdDelete**](BYOKApi.md#revokepublickeyapiv1byokpublickeyskeyiddelete) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key |
| [**revokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0**](BYOKApi.md#revokepublickeyapiv1byokpublickeyskeyiddelete_0) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key |



## listPublicKeysApiV1ByokPublicKeysGet

> PublicKeyListResponse listPublicKeysApiV1ByokPublicKeysGet(includeRevoked)

List public keys

List all registered public keys for the organization.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { ListPublicKeysApiV1ByokPublicKeysGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // boolean | Include revoked keys (optional)
    includeRevoked: true,
  } satisfies ListPublicKeysApiV1ByokPublicKeysGetRequest;

  try {
    const data = await api.listPublicKeysApiV1ByokPublicKeysGet(body);
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

[**PublicKeyListResponse**](PublicKeyListResponse.md)

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


## listPublicKeysApiV1ByokPublicKeysGet_0

> PublicKeyListResponse listPublicKeysApiV1ByokPublicKeysGet_0(includeRevoked)

List public keys

List all registered public keys for the organization.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { ListPublicKeysApiV1ByokPublicKeysGet0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // boolean | Include revoked keys (optional)
    includeRevoked: true,
  } satisfies ListPublicKeysApiV1ByokPublicKeysGet0Request;

  try {
    const data = await api.listPublicKeysApiV1ByokPublicKeysGet_0(body);
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

[**PublicKeyListResponse**](PublicKeyListResponse.md)

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


## registerPublicKeyApiV1ByokPublicKeysPost

> PublicKeyRegisterResponse registerPublicKeyApiV1ByokPublicKeysPost(publicKeyRegisterRequest)

Register a public key

Register a BYOK public key for signature verification.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { RegisterPublicKeyApiV1ByokPublicKeysPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // PublicKeyRegisterRequest
    publicKeyRegisterRequest: ...,
  } satisfies RegisterPublicKeyApiV1ByokPublicKeysPostRequest;

  try {
    const data = await api.registerPublicKeyApiV1ByokPublicKeysPost(body);
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
| **publicKeyRegisterRequest** | [PublicKeyRegisterRequest](PublicKeyRegisterRequest.md) |  | |

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

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


## registerPublicKeyApiV1ByokPublicKeysPost_0

> PublicKeyRegisterResponse registerPublicKeyApiV1ByokPublicKeysPost_0(publicKeyRegisterRequest)

Register a public key

Register a BYOK public key for signature verification.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { RegisterPublicKeyApiV1ByokPublicKeysPost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // PublicKeyRegisterRequest
    publicKeyRegisterRequest: ...,
  } satisfies RegisterPublicKeyApiV1ByokPublicKeysPost0Request;

  try {
    const data = await api.registerPublicKeyApiV1ByokPublicKeysPost_0(body);
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
| **publicKeyRegisterRequest** | [PublicKeyRegisterRequest](PublicKeyRegisterRequest.md) |  | |

### Return type

[**PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

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


## revokePublicKeyApiV1ByokPublicKeysKeyIdDelete

> { [key: string]: any; } revokePublicKeyApiV1ByokPublicKeysKeyIdDelete(keyId, reason)

Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { RevokePublicKeyApiV1ByokPublicKeysKeyIdDeleteRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // string
    keyId: keyId_example,
    // string | Reason for revocation (optional)
    reason: reason_example,
  } satisfies RevokePublicKeyApiV1ByokPublicKeysKeyIdDeleteRequest;

  try {
    const data = await api.revokePublicKeyApiV1ByokPublicKeysKeyIdDelete(body);
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
| **reason** | `string` | Reason for revocation | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: any; }**

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


## revokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0

> { [key: string]: any; } revokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0(keyId, reason)

Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Example

```ts
import {
  Configuration,
  BYOKApi,
} from '@encypher/sdk';
import type { RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new BYOKApi(config);

  const body = {
    // string
    keyId: keyId_example,
    // string | Reason for revocation (optional)
    reason: reason_example,
  } satisfies RevokePublicKeyApiV1ByokPublicKeysKeyIdDelete0Request;

  try {
    const data = await api.revokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0(body);
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
| **reason** | `string` | Reason for revocation | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: any; }**

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

