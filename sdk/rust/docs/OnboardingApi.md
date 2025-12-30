# \OnboardingApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_certificate_status_api_v1_onboarding_certificate_status_get**](OnboardingApi.md#get_certificate_status_api_v1_onboarding_certificate_status_get) | **GET** /api/v1/onboarding/certificate-status | Get Certificate Status
[**request_certificate_api_v1_onboarding_request_certificate_post**](OnboardingApi.md#request_certificate_api_v1_onboarding_request_certificate_post) | **POST** /api/v1/onboarding/request-certificate | Request Certificate



## get_certificate_status_api_v1_onboarding_certificate_status_get

> serde_json::Value get_certificate_status_api_v1_onboarding_certificate_status_get()
Get Certificate Status

Get current certificate status for organization.  Args:     organization: Organization details from authentication     db: Database session  Returns:     dict: Current certificate status

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## request_certificate_api_v1_onboarding_request_certificate_post

> serde_json::Value request_certificate_api_v1_onboarding_request_certificate_post()
Request Certificate

Initiate SSL.com certificate request for organization.  This endpoint: 1. Checks if organization already has a pending/active certificate 2. Creates SSL.com order via API 3. Stores order tracking in certificate_lifecycle table 4. Returns validation URL to organization  Args:     organization: Organization details from authentication     db: Database session  Returns:     dict: Certificate request details including validation URL  Raises:     HTTPException: If organization already has certificate or SSL.com API fails

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

