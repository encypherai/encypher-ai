# \MultiSourceAttributionApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**multi_source_lookup_api_v1_enterprise_attribution_multi_source_post**](MultiSourceAttributionApi.md#multi_source_lookup_api_v1_enterprise_attribution_multi_source_post) | **POST** /api/v1/enterprise/attribution/multi-source | Multi Source Lookup



## multi_source_lookup_api_v1_enterprise_attribution_multi_source_post

> models::MultiSourceLookupResponse multi_source_lookup_api_v1_enterprise_attribution_multi_source_post(multi_source_lookup_request)
Multi Source Lookup

Look up content across multiple sources.  Returns all matching sources with linked-list tracking, chronological ordering, and optional authority ranking.  **Tier Requirement:** Business+ (Authority ranking requires Enterprise)  Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**multi_source_lookup_request** | [**MultiSourceLookupRequest**](MultiSourceLookupRequest.md) |  | [required] |

### Return type

[**models::MultiSourceLookupResponse**](MultiSourceLookupResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

