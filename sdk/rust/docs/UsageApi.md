# \UsageApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_usage_history_api_v1_usage_history_get**](UsageApi.md#get_usage_history_api_v1_usage_history_get) | **GET** /api/v1/usage/history | Get Usage History
[**get_usage_stats_api_v1_usage_get**](UsageApi.md#get_usage_stats_api_v1_usage_get) | **GET** /api/v1/usage | Get Usage Stats
[**reset_monthly_usage_api_v1_usage_reset_post**](UsageApi.md#reset_monthly_usage_api_v1_usage_reset_post) | **POST** /api/v1/usage/reset | Reset Monthly Usage



## get_usage_history_api_v1_usage_history_get

> serde_json::Value get_usage_history_api_v1_usage_history_get(months)
Get Usage History

Get historical usage data for the organization.  Returns monthly usage summaries for the specified number of months.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**months** | Option<**i32**> |  |  |[default to 6]

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_usage_stats_api_v1_usage_get

> models::UsageResponse get_usage_stats_api_v1_usage_get()
Get Usage Stats

Get current period usage statistics for the organization.  Returns usage metrics including: - C2PA signatures (documents signed) - Sentences tracked - Batch operations - API calls

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::UsageResponse**](UsageResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## reset_monthly_usage_api_v1_usage_reset_post

> models::UsageResetResponse reset_monthly_usage_api_v1_usage_reset_post()
Reset Monthly Usage

Reset monthly usage counters.  This is typically called by a scheduled job at the start of each billing period. Requires admin permissions.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::UsageResetResponse**](UsageResetResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

