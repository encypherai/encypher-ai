# \StatusRevocationApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_document_status_api_v1_status_documents_document_id_get**](StatusRevocationApi.md#get_document_status_api_v1_status_documents_document_id_get) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
[**get_document_status_api_v1_status_documents_document_id_get_0**](StatusRevocationApi.md#get_document_status_api_v1_status_documents_document_id_get_0) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
[**get_status_list_api_v1_status_list_organization_id_list_index_get**](StatusRevocationApi.md#get_status_list_api_v1_status_list_organization_id_list_index_get) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**get_status_list_api_v1_status_list_organization_id_list_index_get_0**](StatusRevocationApi.md#get_status_list_api_v1_status_list_organization_id_list_index_get_0) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
[**get_status_stats_api_v1_status_stats_get**](StatusRevocationApi.md#get_status_stats_api_v1_status_stats_get) | **GET** /api/v1/status/stats | Get Status Stats
[**get_status_stats_api_v1_status_stats_get_0**](StatusRevocationApi.md#get_status_stats_api_v1_status_stats_get_0) | **GET** /api/v1/status/stats | Get Status Stats
[**reinstate_document_api_v1_status_documents_document_id_reinstate_post**](StatusRevocationApi.md#reinstate_document_api_v1_status_documents_document_id_reinstate_post) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**reinstate_document_api_v1_status_documents_document_id_reinstate_post_0**](StatusRevocationApi.md#reinstate_document_api_v1_status_documents_document_id_reinstate_post_0) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
[**revoke_document_api_v1_status_documents_document_id_revoke_post**](StatusRevocationApi.md#revoke_document_api_v1_status_documents_document_id_revoke_post) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document
[**revoke_document_api_v1_status_documents_document_id_revoke_post_0**](StatusRevocationApi.md#revoke_document_api_v1_status_documents_document_id_revoke_post_0) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document



## get_document_status_api_v1_status_documents_document_id_get

> models::DocumentStatusResponse get_document_status_api_v1_status_documents_document_id_get(document_id)
Get Document Status

Get the revocation status of a document.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_document_status_api_v1_status_documents_document_id_get_0

> models::DocumentStatusResponse get_document_status_api_v1_status_documents_document_id_get_0(document_id)
Get Document Status

Get the revocation status of a document.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentStatusResponse**](DocumentStatusResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_status_list_api_v1_status_list_organization_id_list_index_get

> serde_json::Value get_status_list_api_v1_status_list_organization_id_list_index_get(organization_id, list_index)
Get Status List

Get a status list credential (public, no auth required).  This endpoint serves W3C StatusList2021 credentials for verification. Responses are designed to be cached by CDN with 5-minute TTL.  **Response Format:** W3C StatusList2021Credential (JSON-LD)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**organization_id** | **String** |  | [required] |
**list_index** | **i32** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_status_list_api_v1_status_list_organization_id_list_index_get_0

> serde_json::Value get_status_list_api_v1_status_list_organization_id_list_index_get_0(organization_id, list_index)
Get Status List

Get a status list credential (public, no auth required).  This endpoint serves W3C StatusList2021 credentials for verification. Responses are designed to be cached by CDN with 5-minute TTL.  **Response Format:** W3C StatusList2021Credential (JSON-LD)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**organization_id** | **String** |  | [required] |
**list_index** | **i32** |  | [required] |

### Return type

[**serde_json::Value**](serde_json::Value.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_status_stats_api_v1_status_stats_get

> serde_json::Value get_status_stats_api_v1_status_stats_get()
Get Status Stats

Get status list statistics for the organization.

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


## get_status_stats_api_v1_status_stats_get_0

> serde_json::Value get_status_stats_api_v1_status_stats_get_0()
Get Status Stats

Get status list statistics for the organization.

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


## reinstate_document_api_v1_status_documents_document_id_reinstate_post

> models::RevocationResponse reinstate_document_api_v1_status_documents_document_id_reinstate_post(document_id)
Reinstate Document

Reinstate a previously revoked document.  The document will pass verification again within 5 minutes (CDN cache TTL).

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## reinstate_document_api_v1_status_documents_document_id_reinstate_post_0

> models::RevocationResponse reinstate_document_api_v1_status_documents_document_id_reinstate_post_0(document_id)
Reinstate Document

Reinstate a previously revoked document.  The document will pass verification again within 5 minutes (CDN cache TTL).

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_document_api_v1_status_documents_document_id_revoke_post

> models::RevocationResponse revoke_document_api_v1_status_documents_document_id_revoke_post(document_id, revoke_request)
Revoke Document

Revoke a document's authenticity.  The document will fail verification within 5 minutes (CDN cache TTL). This action is reversible via the reinstate endpoint.  **Revocation Reasons:** - `factual_error`: Content contains factual errors - `legal_takedown`: Legal request (DMCA, court order) - `copyright_claim`: Copyright infringement claim - `privacy_request`: Privacy/GDPR request - `publisher_request`: Publisher-initiated takedown - `security_concern`: Security vulnerability in content - `content_policy`: Violates content policy - `other`: Other reason (specify in reason_detail)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |
**revoke_request** | [**RevokeRequest**](RevokeRequest.md) |  | [required] |

### Return type

[**models::RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_document_api_v1_status_documents_document_id_revoke_post_0

> models::RevocationResponse revoke_document_api_v1_status_documents_document_id_revoke_post_0(document_id, revoke_request)
Revoke Document

Revoke a document's authenticity.  The document will fail verification within 5 minutes (CDN cache TTL). This action is reversible via the reinstate endpoint.  **Revocation Reasons:** - `factual_error`: Content contains factual errors - `legal_takedown`: Legal request (DMCA, court order) - `copyright_claim`: Copyright infringement claim - `privacy_request`: Privacy/GDPR request - `publisher_request`: Publisher-initiated takedown - `security_concern`: Security vulnerability in content - `content_policy`: Violates content policy - `other`: Other reason (specify in reason_detail)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |
**revoke_request** | [**RevokeRequest**](RevokeRequest.md) |  | [required] |

### Return type

[**models::RevocationResponse**](RevocationResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
