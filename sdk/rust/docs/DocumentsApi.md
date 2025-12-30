# \DocumentsApi

All URIs are relative to *https://api.encypherai.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_document_api_v1_documents_document_id_delete**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**delete_document_api_v1_documents_document_id_delete_0**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**get_document_api_v1_documents_document_id_get**](DocumentsApi.md#get_document_api_v1_documents_document_id_get) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_api_v1_documents_document_id_get_0**](DocumentsApi.md#get_document_api_v1_documents_document_id_get_0) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_history_api_v1_documents_document_id_history_get**](DocumentsApi.md#get_document_history_api_v1_documents_document_id_history_get) | **GET** /api/v1/documents/{document_id}/history | Get Document History
[**get_document_history_api_v1_documents_document_id_history_get_0**](DocumentsApi.md#get_document_history_api_v1_documents_document_id_history_get_0) | **GET** /api/v1/documents/{document_id}/history | Get Document History
[**list_documents_api_v1_documents_get**](DocumentsApi.md#list_documents_api_v1_documents_get) | **GET** /api/v1/documents | List Documents
[**list_documents_api_v1_documents_get_0**](DocumentsApi.md#list_documents_api_v1_documents_get_0) | **GET** /api/v1/documents | List Documents



## delete_document_api_v1_documents_document_id_delete

> models::DocumentDeleteResponse delete_document_api_v1_documents_document_id_delete(document_id, revoke, reason)
Delete Document

Soft delete a document.  By default, this also revokes the document so it will fail verification. The document is not permanently deleted but marked as deleted.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |
**revoke** | Option<**bool**> | Also revoke the document |  |[default to true]
**reason** | Option<**String**> | Reason for deletion |  |

### Return type

[**models::DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## delete_document_api_v1_documents_document_id_delete_0

> models::DocumentDeleteResponse delete_document_api_v1_documents_document_id_delete_0(document_id, revoke, reason)
Delete Document

Soft delete a document.  By default, this also revokes the document so it will fail verification. The document is not permanently deleted but marked as deleted.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |
**revoke** | Option<**bool**> | Also revoke the document |  |[default to true]
**reason** | Option<**String**> | Reason for deletion |  |

### Return type

[**models::DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_document_api_v1_documents_document_id_get

> models::DocumentDetailResponse get_document_api_v1_documents_document_id_get(document_id)
Get Document

Get detailed information about a specific document.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_document_api_v1_documents_document_id_get_0

> models::DocumentDetailResponse get_document_api_v1_documents_document_id_get_0(document_id)
Get Document

Get detailed information about a specific document.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentDetailResponse**](DocumentDetailResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_document_history_api_v1_documents_document_id_history_get

> models::DocumentHistoryResponse get_document_history_api_v1_documents_document_id_history_get(document_id)
Get Document History

Get the audit trail/history for a document.  Shows all actions taken on the document including signing, verification, and revocation.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_document_history_api_v1_documents_document_id_history_get_0

> models::DocumentHistoryResponse get_document_history_api_v1_documents_document_id_history_get_0(document_id)
Get Document History

Get the audit trail/history for a document.  Shows all actions taken on the document including signing, verification, and revocation.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**document_id** | **String** |  | [required] |

### Return type

[**models::DocumentHistoryResponse**](DocumentHistoryResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_documents_api_v1_documents_get

> models::DocumentListResponse list_documents_api_v1_documents_get(page, page_size, search, status, from_date, to_date)
List Documents

List signed documents for the organization.  Supports pagination, search, and filtering by status and date range.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**page** | Option<**i32**> | Page number |  |[default to 1]
**page_size** | Option<**i32**> | Items per page |  |[default to 50]
**search** | Option<**String**> | Search in title |  |
**status** | Option<**String**> | Filter by status (active/revoked) |  |
**from_date** | Option<**String**> | Filter from date (ISO format) |  |
**to_date** | Option<**String**> | Filter to date (ISO format) |  |

### Return type

[**models::DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_documents_api_v1_documents_get_0

> models::DocumentListResponse list_documents_api_v1_documents_get_0(page, page_size, search, status, from_date, to_date)
List Documents

List signed documents for the organization.  Supports pagination, search, and filtering by status and date range.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**page** | Option<**i32**> | Page number |  |[default to 1]
**page_size** | Option<**i32**> | Items per page |  |[default to 50]
**search** | Option<**String**> | Search in title |  |
**status** | Option<**String**> | Filter by status (active/revoked) |  |
**from_date** | Option<**String**> | Filter from date (ISO format) |  |
**to_date** | Option<**String**> | Filter to date (ISO format) |  |

### Return type

[**models::DocumentListResponse**](DocumentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

