# FingerprintApi

All URIs are relative to *https://api.encypherai.com*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**detectFingerprintApiV1EnterpriseFingerprintDetectPost**](FingerprintApi.md#detectfingerprintapiv1enterprisefingerprintdetectpost) | **POST** /api/v1/enterprise/fingerprint/detect | Detect Fingerprint |
| [**encodeFingerprintApiV1EnterpriseFingerprintEncodePost**](FingerprintApi.md#encodefingerprintapiv1enterprisefingerprintencodepost) | **POST** /api/v1/enterprise/fingerprint/encode | Encode Fingerprint |



## detectFingerprintApiV1EnterpriseFingerprintDetectPost

> FingerprintDetectResponse detectFingerprintApiV1EnterpriseFingerprintDetectPost(fingerprintDetectRequest)

Detect Fingerprint

Detect a fingerprint in text.  Detection uses score-based matching with confidence threshold to identify fingerprinted content even after modifications.  **Tier Requirement:** Enterprise

### Example

```ts
import {
  Configuration,
  FingerprintApi,
} from '@encypher/sdk';
import type { DetectFingerprintApiV1EnterpriseFingerprintDetectPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new FingerprintApi(config);

  const body = {
    // FingerprintDetectRequest
    fingerprintDetectRequest: ...,
  } satisfies DetectFingerprintApiV1EnterpriseFingerprintDetectPostRequest;

  try {
    const data = await api.detectFingerprintApiV1EnterpriseFingerprintDetectPost(body);
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
| **fingerprintDetectRequest** | [FingerprintDetectRequest](FingerprintDetectRequest.md) |  | |

### Return type

[**FingerprintDetectResponse**](FingerprintDetectResponse.md)

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


## encodeFingerprintApiV1EnterpriseFingerprintEncodePost

> FingerprintEncodeResponse encodeFingerprintApiV1EnterpriseFingerprintEncodePost(fingerprintEncodeRequest)

Encode Fingerprint

Encode a robust fingerprint into text.  Fingerprints use secret-seeded placement of invisible markers that survive text modifications like paraphrasing or truncation.  **Tier Requirement:** Enterprise

### Example

```ts
import {
  Configuration,
  FingerprintApi,
} from '@encypher/sdk';
import type { EncodeFingerprintApiV1EnterpriseFingerprintEncodePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new FingerprintApi(config);

  const body = {
    // FingerprintEncodeRequest
    fingerprintEncodeRequest: ...,
  } satisfies EncodeFingerprintApiV1EnterpriseFingerprintEncodePostRequest;

  try {
    const data = await api.encodeFingerprintApiV1EnterpriseFingerprintEncodePost(body);
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
| **fingerprintEncodeRequest** | [FingerprintEncodeRequest](FingerprintEncodeRequest.md) |  | |

### Return type

[**FingerprintEncodeResponse**](FingerprintEncodeResponse.md)

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

