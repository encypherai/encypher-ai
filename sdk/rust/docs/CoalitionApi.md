# \CoalitionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_coalition_dashboard_api_v1_coalition_dashboard_get**](CoalitionApi.md#get_coalition_dashboard_api_v1_coalition_dashboard_get) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**get_coalition_dashboard_api_v1_coalition_dashboard_get_0**](CoalitionApi.md#get_coalition_dashboard_api_v1_coalition_dashboard_get_0) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
[**get_content_stats_api_v1_coalition_content_stats_get**](CoalitionApi.md#get_content_stats_api_v1_coalition_content_stats_get) | **GET** /api/v1/coalition/content-stats | Get Content Stats
[**get_content_stats_api_v1_coalition_content_stats_get_0**](CoalitionApi.md#get_content_stats_api_v1_coalition_content_stats_get_0) | **GET** /api/v1/coalition/content-stats | Get Content Stats
[**get_earnings_history_api_v1_coalition_earnings_get**](CoalitionApi.md#get_earnings_history_api_v1_coalition_earnings_get) | **GET** /api/v1/coalition/earnings | Get Earnings History
[**get_earnings_history_api_v1_coalition_earnings_get_0**](CoalitionApi.md#get_earnings_history_api_v1_coalition_earnings_get_0) | **GET** /api/v1/coalition/earnings | Get Earnings History
[**opt_in_to_coalition_api_v1_coalition_opt_in_post**](CoalitionApi.md#opt_in_to_coalition_api_v1_coalition_opt_in_post) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
[**opt_in_to_coalition_api_v1_coalition_opt_in_post_0**](CoalitionApi.md#opt_in_to_coalition_api_v1_coalition_opt_in_post_0) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
[**opt_out_of_coalition_api_v1_coalition_opt_out_post**](CoalitionApi.md#opt_out_of_coalition_api_v1_coalition_opt_out_post) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition
[**opt_out_of_coalition_api_v1_coalition_opt_out_post_0**](CoalitionApi.md#opt_out_of_coalition_api_v1_coalition_opt_out_post_0) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition



## get_coalition_dashboard_api_v1_coalition_dashboard_get

> models::CoalitionDashboardResponse get_coalition_dashboard_api_v1_coalition_dashboard_get()
Get Coalition Dashboard

Get coalition dashboard data for the organization.  Returns content stats, earnings, and payout information.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_coalition_dashboard_api_v1_coalition_dashboard_get_0

> models::CoalitionDashboardResponse get_coalition_dashboard_api_v1_coalition_dashboard_get_0()
Get Coalition Dashboard

Get coalition dashboard data for the organization.  Returns content stats, earnings, and payout information.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::CoalitionDashboardResponse**](CoalitionDashboardResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_content_stats_api_v1_coalition_content_stats_get

> serde_json::Value get_content_stats_api_v1_coalition_content_stats_get(months)
Get Content Stats

Get historical content corpus statistics.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**months** | Option<**i32**> |  |  |[default to 12]

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_content_stats_api_v1_coalition_content_stats_get_0

> serde_json::Value get_content_stats_api_v1_coalition_content_stats_get_0(months)
Get Content Stats

Get historical content corpus statistics.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**months** | Option<**i32**> |  |  |[default to 12]

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_earnings_history_api_v1_coalition_earnings_get

> serde_json::Value get_earnings_history_api_v1_coalition_earnings_get(months)
Get Earnings History

Get detailed earnings history.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**months** | Option<**i32**> |  |  |[default to 12]

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_earnings_history_api_v1_coalition_earnings_get_0

> serde_json::Value get_earnings_history_api_v1_coalition_earnings_get_0(months)
Get Earnings History

Get detailed earnings history.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**months** | Option<**i32**> |  |  |[default to 12]

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## opt_in_to_coalition_api_v1_coalition_opt_in_post

> serde_json::Value opt_in_to_coalition_api_v1_coalition_opt_in_post()
Opt In To Coalition

Opt back into the coalition revenue sharing program.

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


## opt_in_to_coalition_api_v1_coalition_opt_in_post_0

> serde_json::Value opt_in_to_coalition_api_v1_coalition_opt_in_post_0()
Opt In To Coalition

Opt back into the coalition revenue sharing program.

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


## opt_out_of_coalition_api_v1_coalition_opt_out_post

> serde_json::Value opt_out_of_coalition_api_v1_coalition_opt_out_post()
Opt Out Of Coalition

Opt out of the coalition revenue sharing program.  Note: This will stop future earnings but won't affect pending payouts.

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


## opt_out_of_coalition_api_v1_coalition_opt_out_post_0

> serde_json::Value opt_out_of_coalition_api_v1_coalition_opt_out_post_0()
Opt Out Of Coalition

Opt out of the coalition revenue sharing program.  Note: This will stop future earnings but won't affect pending payouts.

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

