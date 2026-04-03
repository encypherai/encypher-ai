# \HealthApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check_health_get**](HealthApi.md#health_check_health_get) | **GET** /health | Health Check
[**readiness_check_readyz_get**](HealthApi.md#readiness_check_readyz_get) | **GET** /readyz | Readiness Check



## health_check_health_get

> serde_json::Value health_check_health_get()
Health Check

Health check endpoint for monitoring.  Returns:     dict: Status and environment information

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## readiness_check_readyz_get

> serde_json::Value readiness_check_readyz_get()
Readiness Check

Lightweight readiness probe.

### Parameters

This endpoint does not need any parameter.

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
