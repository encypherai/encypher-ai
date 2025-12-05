# PublicToolsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**decodeTextApiV1ToolsDecodePost**](PublicToolsApi.md#decodetextapiv1toolsdecodepost) | **POST** /api/v1/tools/decode | Decode Text |
| [**decodeTextApiV1ToolsDecodePost_0**](PublicToolsApi.md#decodetextapiv1toolsdecodepost_0) | **POST** /api/v1/tools/decode | Decode Text |
| [**encodeTextApiV1ToolsEncodePost**](PublicToolsApi.md#encodetextapiv1toolsencodepost) | **POST** /api/v1/tools/encode | Encode Text |
| [**encodeTextApiV1ToolsEncodePost_0**](PublicToolsApi.md#encodetextapiv1toolsencodepost_0) | **POST** /api/v1/tools/encode | Encode Text |



## decodeTextApiV1ToolsDecodePost

> DecodeToolResponse decodeTextApiV1ToolsDecodePost(decodeToolRequest)

Decode Text

Decode and verify text containing embedded metadata.  This is a public endpoint for the website demo tool. Verification uses the demo public key.

### Example

```ts
import {
  Configuration,
  PublicToolsApi,
} from '@encypher/sdk';
import type { DecodeTextApiV1ToolsDecodePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicToolsApi();

  const body = {
    // DecodeToolRequest
    decodeToolRequest: ...,
  } satisfies DecodeTextApiV1ToolsDecodePostRequest;

  try {
    const data = await api.decodeTextApiV1ToolsDecodePost(body);
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
| **decodeToolRequest** | [DecodeToolRequest](DecodeToolRequest.md) |  | |

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

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


## decodeTextApiV1ToolsDecodePost_0

> DecodeToolResponse decodeTextApiV1ToolsDecodePost_0(decodeToolRequest)

Decode Text

Decode and verify text containing embedded metadata.  This is a public endpoint for the website demo tool. Verification uses the demo public key.

### Example

```ts
import {
  Configuration,
  PublicToolsApi,
} from '@encypher/sdk';
import type { DecodeTextApiV1ToolsDecodePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicToolsApi();

  const body = {
    // DecodeToolRequest
    decodeToolRequest: ...,
  } satisfies DecodeTextApiV1ToolsDecodePost0Request;

  try {
    const data = await api.decodeTextApiV1ToolsDecodePost_0(body);
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
| **decodeToolRequest** | [DecodeToolRequest](DecodeToolRequest.md) |  | |

### Return type

[**DecodeToolResponse**](DecodeToolResponse.md)

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


## encodeTextApiV1ToolsEncodePost

> EncodeToolResponse encodeTextApiV1ToolsEncodePost(encodeToolRequest)

Encode Text

Encode text with embedded metadata using the demo key.  This is a public endpoint for the website demo tool. All encoding uses a server-side demo key.

### Example

```ts
import {
  Configuration,
  PublicToolsApi,
} from '@encypher/sdk';
import type { EncodeTextApiV1ToolsEncodePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicToolsApi();

  const body = {
    // EncodeToolRequest
    encodeToolRequest: ...,
  } satisfies EncodeTextApiV1ToolsEncodePostRequest;

  try {
    const data = await api.encodeTextApiV1ToolsEncodePost(body);
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
| **encodeToolRequest** | [EncodeToolRequest](EncodeToolRequest.md) |  | |

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

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


## encodeTextApiV1ToolsEncodePost_0

> EncodeToolResponse encodeTextApiV1ToolsEncodePost_0(encodeToolRequest)

Encode Text

Encode text with embedded metadata using the demo key.  This is a public endpoint for the website demo tool. All encoding uses a server-side demo key.

### Example

```ts
import {
  Configuration,
  PublicToolsApi,
} from '@encypher/sdk';
import type { EncodeTextApiV1ToolsEncodePost0Request } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const api = new PublicToolsApi();

  const body = {
    // EncodeToolRequest
    encodeToolRequest: ...,
  } satisfies EncodeTextApiV1ToolsEncodePost0Request;

  try {
    const data = await api.encodeTextApiV1ToolsEncodePost_0(body);
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
| **encodeToolRequest** | [EncodeToolRequest](EncodeToolRequest.md) |  | |

### Return type

[**EncodeToolResponse**](EncodeToolResponse.md)

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

