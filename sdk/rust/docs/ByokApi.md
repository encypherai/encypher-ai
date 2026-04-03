# \ByokApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_public_keys_api_v1_byok_public_keys_get**](ByokApi.md#list_public_keys_api_v1_byok_public_keys_get) | **GET** /api/v1/byok/public-keys | List public keys
[**list_public_keys_api_v1_byok_public_keys_get_0**](ByokApi.md#list_public_keys_api_v1_byok_public_keys_get_0) | **GET** /api/v1/byok/public-keys | List public keys
[**list_trusted_cas_api_v1_byok_trusted_cas_get**](ByokApi.md#list_trusted_cas_api_v1_byok_trusted_cas_get) | **GET** /api/v1/byok/trusted-cas | List trusted Certificate Authorities
[**list_trusted_cas_api_v1_byok_trusted_cas_get_0**](ByokApi.md#list_trusted_cas_api_v1_byok_trusted_cas_get_0) | **GET** /api/v1/byok/trusted-cas | List trusted Certificate Authorities
[**register_public_key_api_v1_byok_public_keys_post**](ByokApi.md#register_public_key_api_v1_byok_public_keys_post) | **POST** /api/v1/byok/public-keys | Register a public key
[**register_public_key_api_v1_byok_public_keys_post_0**](ByokApi.md#register_public_key_api_v1_byok_public_keys_post_0) | **POST** /api/v1/byok/public-keys | Register a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete**](ByokApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**revoke_public_key_api_v1_byok_public_keys_key_id_delete_0**](ByokApi.md#revoke_public_key_api_v1_byok_public_keys_key_id_delete_0) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
[**upload_certificate_api_v1_byok_certificates_post**](ByokApi.md#upload_certificate_api_v1_byok_certificates_post) | **POST** /api/v1/byok/certificates | Upload a CA-signed certificate
[**upload_certificate_api_v1_byok_certificates_post_0**](ByokApi.md#upload_certificate_api_v1_byok_certificates_post_0) | **POST** /api/v1/byok/certificates | Upload a CA-signed certificate



## list_public_keys_api_v1_byok_public_keys_get

> models::PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get(include_revoked)
List public keys

List all registered public keys for the organization.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_public_keys_api_v1_byok_public_keys_get_0

> models::PublicKeyListResponse list_public_keys_api_v1_byok_public_keys_get_0(include_revoked)
List public keys

List all registered public keys for the organization.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**include_revoked** | Option<**bool**> | Include revoked keys |  |[default to false]

### Return type

[**models::PublicKeyListResponse**](PublicKeyListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_trusted_cas_api_v1_byok_trusted_cas_get

> models::TrustListResponse list_trusted_cas_api_v1_byok_trusted_cas_get()
List trusted Certificate Authorities

Returns the list of C2PA-trusted CAs that can issue signing certificates.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::TrustListResponse**](TrustListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_trusted_cas_api_v1_byok_trusted_cas_get_0

> models::TrustListResponse list_trusted_cas_api_v1_byok_trusted_cas_get_0()
List trusted Certificate Authorities

Returns the list of C2PA-trusted CAs that can issue signing certificates.

### Parameters

This endpoint does not need any parameter.

### Return type

[**models::TrustListResponse**](TrustListResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## register_public_key_api_v1_byok_public_keys_post

> models::PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post(public_key_register_request)
Register a public key

Register a BYOK public key for signature verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | [required] |

### Return type

[**models::PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## register_public_key_api_v1_byok_public_keys_post_0

> models::PublicKeyRegisterResponse register_public_key_api_v1_byok_public_keys_post_0(public_key_register_request)
Register a public key

Register a BYOK public key for signature verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**public_key_register_request** | [**PublicKeyRegisterRequest**](PublicKeyRegisterRequest.md) |  | [required] |

### Return type

[**models::PublicKeyRegisterResponse**](PublicKeyRegisterResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_public_key_api_v1_byok_public_keys_key_id_delete

> std::collections::HashMap<String, serde_json::Value> revoke_public_key_api_v1_byok_public_keys_key_id_delete(key_id, reason)
Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**reason** | Option<**String**> | Reason for revocation |  |

### Return type

[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## revoke_public_key_api_v1_byok_public_keys_key_id_delete_0

> std::collections::HashMap<String, serde_json::Value> revoke_public_key_api_v1_byok_public_keys_key_id_delete_0(key_id, reason)
Revoke a public key

Revoke a registered public key. Revoked keys cannot be used for verification.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**key_id** | **String** |  | [required] |
**reason** | Option<**String**> | Reason for revocation |  |

### Return type

[**std::collections::HashMap<String, serde_json::Value>**](serde_json::Value.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## upload_certificate_api_v1_byok_certificates_post

> models::CertificateUploadResponse upload_certificate_api_v1_byok_certificates_post(certificate_upload_request)
Upload a CA-signed certificate

Upload an X.509 certificate signed by a C2PA-trusted CA for BYOK signing.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**certificate_upload_request** | [**CertificateUploadRequest**](CertificateUploadRequest.md) |  | [required] |

### Return type

[**models::CertificateUploadResponse**](CertificateUploadResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## upload_certificate_api_v1_byok_certificates_post_0

> models::CertificateUploadResponse upload_certificate_api_v1_byok_certificates_post_0(certificate_upload_request)
Upload a CA-signed certificate

Upload an X.509 certificate signed by a C2PA-trusted CA for BYOK signing.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**certificate_upload_request** | [**CertificateUploadRequest**](CertificateUploadRequest.md) |  | [required] |

### Return type

[**models::CertificateUploadResponse**](CertificateUploadResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
