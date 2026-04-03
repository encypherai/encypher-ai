# \AccountApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_account_info_api_v1_account_get**](AccountApi.md#get_account_info_api_v1_account_get) | **GET** /api/v1/account | Get Account Info
[**get_account_info_api_v1_account_get_0**](AccountApi.md#get_account_info_api_v1_account_get_0) | **GET** /api/v1/account | Get Account Info
[**get_account_quota_api_v1_account_quota_get**](AccountApi.md#get_account_quota_api_v1_account_quota_get) | **GET** /api/v1/account/quota | Get Account Quota
[**get_account_quota_api_v1_account_quota_get_0**](AccountApi.md#get_account_quota_api_v1_account_quota_get_0) | **GET** /api/v1/account/quota | Get Account Quota



## get_account_info_api_v1_account_get

> models::AccountResponse get_account_info_api_v1_account_get()
Get Account Info

Get current organization account information.  Returns organization details including: - Organization ID and name - Current subscription tier - Enabled feature flags - Account creation date

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::AccountResponse**](AccountResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_account_info_api_v1_account_get_0

> models::AccountResponse get_account_info_api_v1_account_get_0()
Get Account Info

Get current organization account information.  Returns organization details including: - Organization ID and name - Current subscription tier - Enabled feature flags - Account creation date

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::AccountResponse**](AccountResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_account_quota_api_v1_account_quota_get

> models::QuotaResponse get_account_quota_api_v1_account_quota_get()
Get Account Quota

Get detailed quota information for the organization.  Returns current usage and limits for: - C2PA signatures - Sentences tracked - Batch operations - API calls

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::QuotaResponse**](QuotaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_account_quota_api_v1_account_quota_get_0

> models::QuotaResponse get_account_quota_api_v1_account_quota_get_0()
Get Account Quota

Get detailed quota information for the organization.  Returns current usage and limits for: - C2PA signatures - Sentences tracked - Batch operations - API calls

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::QuotaResponse**](QuotaResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
