# PublicC2PAApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createManifestApiV1PublicC2paCreateManifestPost**](PublicC2PAApi.md#createmanifestapiv1publicc2pacreatemanifestpost) | **POST** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic) |
| [**getTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet**](PublicC2PAApi.md#gettrustanchorapiv1publicc2patrustanchorssigneridget) | **GET** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public) |
| [**validateManifestApiV1PublicC2paValidateManifestPost**](PublicC2PAApi.md#validatemanifestapiv1publicc2pavalidatemanifestpost) | **POST** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic) |



## createManifestApiV1PublicC2paCreateManifestPost

> CreateManifestResponse createManifestApiV1PublicC2paCreateManifestPost(createManifestRequest, authorization)

Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)

Create a C2PA-like manifest JSON payload from plaintext. This endpoint is intended for client-side workflows that want a server-generated starting point for a manifest before cryptographic signing.  Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Example

```ts
import {
  Configuration,
  PublicC2PAApi,
} from '@encypher/sdk';
import type { CreateManifestApiV1PublicC2paCreateManifestPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicC2PAApi();

  const body = {
    // CreateManifestRequest
    createManifestRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies CreateManifestApiV1PublicC2paCreateManifestPostRequest;

  try {
    const data = await api.createManifestApiV1PublicC2paCreateManifestPost(body);
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
| **createManifestRequest** | [CreateManifestRequest](CreateManifestRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**CreateManifestResponse**](CreateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet

> TrustAnchorResponse getTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet(signerId)

Lookup trust anchor for C2PA verification (Public)

Lookup a trust anchor (public key) for external C2PA validators.  This endpoint enables third-party validators to verify Encypher-signed content by providing the signer\&#39;s public key. This implements the \&quot;Private Credential Store\&quot; model per C2PA spec §14.4.3.  **Special signer IDs:** - &#x60;encypher.public&#x60; or &#x60;org_demo&#x60;: Returns Encypher\&#39;s official demo/free-tier key - &#x60;demo-*&#x60;: Returns demo/test keys (non-production)  **C2PA Spec Reference:** https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists

### Example

```ts
import {
  Configuration,
  PublicC2PAApi,
} from '@encypher/sdk';
import type { GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicC2PAApi();

  const body = {
    // string | Signer identifier from manifest
    signerId: signerId_example,
  } satisfies GetTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGetRequest;

  try {
    const data = await api.getTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet(body);
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
| **signerId** | `string` | Signer identifier from manifest | [Defaults to `undefined`] |

### Return type

[**TrustAnchorResponse**](TrustAnchorResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **404** | Signer not found |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## validateManifestApiV1PublicC2paValidateManifestPost

> ValidateManifestResponse validateManifestApiV1PublicC2paValidateManifestPost(validateManifestRequest, authorization)

Validate C2PA-like manifest JSON (Public - Non-Cryptographic)

Validate a manifest JSON payload and (optionally) validate assertion payloads against provided JSON Schemas. This endpoint performs structural/schema validation only and does not verify cryptographic signatures.  Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Example

```ts
import {
  Configuration,
  PublicC2PAApi,
} from '@encypher/sdk';
import type { ValidateManifestApiV1PublicC2paValidateManifestPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicC2PAApi();

  const body = {
    // ValidateManifestRequest
    validateManifestRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies ValidateManifestApiV1PublicC2paValidateManifestPostRequest;

  try {
    const data = await api.validateManifestApiV1PublicC2paValidateManifestPost(body);
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
| **validateManifestRequest** | [ValidateManifestRequest](ValidateManifestRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ValidateManifestResponse**](ValidateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

