# OnboardingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getCertificateStatusApiV1OnboardingCertificateStatusGet**](OnboardingApi.md#getcertificatestatusapiv1onboardingcertificatestatusget) | **GET** /api/v1/onboarding/certificate-status | Get Certificate Status |
| [**requestCertificateApiV1OnboardingRequestCertificatePost**](OnboardingApi.md#requestcertificateapiv1onboardingrequestcertificatepost) | **POST** /api/v1/onboarding/request-certificate | Request Certificate |



## getCertificateStatusApiV1OnboardingCertificateStatusGet

> any getCertificateStatusApiV1OnboardingCertificateStatusGet()

Get Certificate Status

Get current certificate status for organization.  Args:     organization: Organization details from authentication     db: Database session  Returns:     dict: Current certificate status

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@encypher/sdk';
import type { GetCertificateStatusApiV1OnboardingCertificateStatusGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OnboardingApi(config);

  try {
    const data = await api.getCertificateStatusApiV1OnboardingCertificateStatusGet();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## requestCertificateApiV1OnboardingRequestCertificatePost

> any requestCertificateApiV1OnboardingRequestCertificatePost()

Request Certificate

Initiate SSL.com certificate request for organization.  This endpoint: 1. Checks if organization already has a pending/active certificate 2. Creates SSL.com order via API 3. Stores order tracking in certificate_lifecycle table 4. Returns validation URL to organization  Args:     organization: Organization details from authentication     db: Database session  Returns:     dict: Certificate request details including validation URL  Raises:     HTTPException: If organization already has certificate or SSL.com API fails

### Example

```ts
import {
  Configuration,
  OnboardingApi,
} from '@encypher/sdk';
import type { RequestCertificateApiV1OnboardingRequestCertificatePostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new OnboardingApi(config);

  try {
    const data = await api.requestCertificateApiV1OnboardingRequestCertificatePost();
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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

