# \WebhooksApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_webhook_api_v1_webhooks_post**](WebhooksApi.md#create_webhook_api_v1_webhooks_post) | **POST** /api/v1/webhooks | Create Webhook
[**create_webhook_api_v1_webhooks_post_0**](WebhooksApi.md#create_webhook_api_v1_webhooks_post_0) | **POST** /api/v1/webhooks | Create Webhook
[**delete_webhook_api_v1_webhooks_webhook_id_delete**](WebhooksApi.md#delete_webhook_api_v1_webhooks_webhook_id_delete) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**delete_webhook_api_v1_webhooks_webhook_id_delete_0**](WebhooksApi.md#delete_webhook_api_v1_webhooks_webhook_id_delete_0) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
[**get_webhook_api_v1_webhooks_webhook_id_get**](WebhooksApi.md#get_webhook_api_v1_webhooks_webhook_id_get) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
[**get_webhook_api_v1_webhooks_webhook_id_get_0**](WebhooksApi.md#get_webhook_api_v1_webhooks_webhook_id_get_0) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
[**get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get**](WebhooksApi.md#get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0**](WebhooksApi.md#get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
[**list_webhooks_api_v1_webhooks_get**](WebhooksApi.md#list_webhooks_api_v1_webhooks_get) | **GET** /api/v1/webhooks | List Webhooks
[**list_webhooks_api_v1_webhooks_get_0**](WebhooksApi.md#list_webhooks_api_v1_webhooks_get_0) | **GET** /api/v1/webhooks | List Webhooks
[**test_webhook_api_v1_webhooks_webhook_id_test_post**](WebhooksApi.md#test_webhook_api_v1_webhooks_webhook_id_test_post) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**test_webhook_api_v1_webhooks_webhook_id_test_post_0**](WebhooksApi.md#test_webhook_api_v1_webhooks_webhook_id_test_post_0) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
[**update_webhook_api_v1_webhooks_webhook_id_patch**](WebhooksApi.md#update_webhook_api_v1_webhooks_webhook_id_patch) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook
[**update_webhook_api_v1_webhooks_webhook_id_patch_0**](WebhooksApi.md#update_webhook_api_v1_webhooks_webhook_id_patch_0) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook



## create_webhook_api_v1_webhooks_post

> models::WebhookCreateResponse create_webhook_api_v1_webhooks_post(webhook_create_request)
Create Webhook

Register a new webhook.  The webhook URL must be HTTPS. You can optionally provide a shared secret for HMAC signature verification of webhook payloads.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_create_request** | [**WebhookCreateRequest**](WebhookCreateRequest.md) |  | [required] |

### Return type

[**models::WebhookCreateResponse**](WebhookCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_webhook_api_v1_webhooks_post_0

> models::WebhookCreateResponse create_webhook_api_v1_webhooks_post_0(webhook_create_request)
Create Webhook

Register a new webhook.  The webhook URL must be HTTPS. You can optionally provide a shared secret for HMAC signature verification of webhook payloads.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_create_request** | [**WebhookCreateRequest**](WebhookCreateRequest.md) |  | [required] |

### Return type

[**models::WebhookCreateResponse**](WebhookCreateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## delete_webhook_api_v1_webhooks_webhook_id_delete

> models::WebhookDeleteResponse delete_webhook_api_v1_webhooks_webhook_id_delete(webhook_id)
Delete Webhook

Delete a webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookDeleteResponse**](WebhookDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## delete_webhook_api_v1_webhooks_webhook_id_delete_0

> models::WebhookDeleteResponse delete_webhook_api_v1_webhooks_webhook_id_delete_0(webhook_id)
Delete Webhook

Delete a webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookDeleteResponse**](WebhookDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_webhook_api_v1_webhooks_webhook_id_get

> models::WebhookListResponse get_webhook_api_v1_webhooks_webhook_id_get(webhook_id)
Get Webhook

Get details of a specific webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_webhook_api_v1_webhooks_webhook_id_get_0

> models::WebhookListResponse get_webhook_api_v1_webhooks_webhook_id_get_0(webhook_id)
Get Webhook

Get details of a specific webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get

> models::WebhookDeliveriesResponse get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get(webhook_id, page, page_size)
Get Webhook Deliveries

Get delivery history for a webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |
**page** | Option<**i32**> |  |  |[default to 1]
**page_size** | Option<**i32**> |  |  |[default to 50]

### Return type

[**models::WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0

> models::WebhookDeliveriesResponse get_webhook_deliveries_api_v1_webhooks_webhook_id_deliveries_get_0(webhook_id, page, page_size)
Get Webhook Deliveries

Get delivery history for a webhook.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |
**page** | Option<**i32**> |  |  |[default to 1]
**page_size** | Option<**i32**> |  |  |[default to 50]

### Return type

[**models::WebhookDeliveriesResponse**](WebhookDeliveriesResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_webhooks_api_v1_webhooks_get

> models::WebhookListResponse list_webhooks_api_v1_webhooks_get()
List Webhooks

List all webhooks for the organization.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_webhooks_api_v1_webhooks_get_0

> models::WebhookListResponse list_webhooks_api_v1_webhooks_get_0()
List Webhooks

List all webhooks for the organization.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::WebhookListResponse**](WebhookListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## test_webhook_api_v1_webhooks_webhook_id_test_post

> models::WebhookTestResponse test_webhook_api_v1_webhooks_webhook_id_test_post(webhook_id)
Test Webhook

Send a test event to the webhook.  This sends a test payload to verify the webhook is configured correctly.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookTestResponse**](WebhookTestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## test_webhook_api_v1_webhooks_webhook_id_test_post_0

> models::WebhookTestResponse test_webhook_api_v1_webhooks_webhook_id_test_post_0(webhook_id)
Test Webhook

Send a test event to the webhook.  This sends a test payload to verify the webhook is configured correctly.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |

### Return type

[**models::WebhookTestResponse**](WebhookTestResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_webhook_api_v1_webhooks_webhook_id_patch

> models::WebhookUpdateResponse update_webhook_api_v1_webhooks_webhook_id_patch(webhook_id, webhook_update_request)
Update Webhook

Update a webhook's URL, events, or active status.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |
**webhook_update_request** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md) |  | [required] |

### Return type

[**models::WebhookUpdateResponse**](WebhookUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_webhook_api_v1_webhooks_webhook_id_patch_0

> models::WebhookUpdateResponse update_webhook_api_v1_webhooks_webhook_id_patch_0(webhook_id, webhook_update_request)
Update Webhook

Update a webhook's URL, events, or active status.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**webhook_id** | **String** |  | [required] |
**webhook_update_request** | [**WebhookUpdateRequest**](WebhookUpdateRequest.md) |  | [required] |

### Return type

[**models::WebhookUpdateResponse**](WebhookUpdateResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

