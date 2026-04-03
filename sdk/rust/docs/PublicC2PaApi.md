# \PublicC2PaApi

All URIs are relative to *https://api.encypher.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_manifest_api_v1_public_c2pa_create_manifest_post**](PublicC2PaApi.md#create_manifest_api_v1_public_c2pa_create_manifest_post) | **POST** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
[**get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get**](PublicC2PaApi.md#get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get) | **GET** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public)
[**validate_manifest_api_v1_public_c2pa_validate_manifest_post**](PublicC2PaApi.md#validate_manifest_api_v1_public_c2pa_validate_manifest_post) | **POST** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic)



## create_manifest_api_v1_public_c2pa_create_manifest_post

> models::CreateManifestResponse create_manifest_api_v1_public_c2pa_create_manifest_post(create_manifest_request, authorization)
Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)

Create a C2PA-like manifest JSON payload from plaintext. This endpoint is intended for client-side workflows that want a server-generated starting point for a manifest before cryptographic signing.  Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**create_manifest_request** | [**CreateManifestRequest**](CreateManifestRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::CreateManifestResponse**](CreateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get

> models::TrustAnchorResponse get_trust_anchor_api_v1_public_c2pa_trust_anchors_signer_id_get(signer_id)
Lookup trust anchor for C2PA verification (Public)

Lookup a trust anchor (public key) for external C2PA validators.  This endpoint enables third-party validators to verify Encypher-signed content by providing the signer's public key. This implements the \"Private Credential Store\" model per C2PA spec §14.4.3.  **Special signer IDs:** - `encypher.public` or `org_demo`: Returns Encypher's official demo/free-tier key - `demo-*`: Returns demo/test keys (non-production)  **C2PA Spec Reference:** https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**signer_id** | **String** | Signer identifier from manifest | [required] |

### Return type

[**models::TrustAnchorResponse**](TrustAnchorResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## validate_manifest_api_v1_public_c2pa_validate_manifest_post

> models::ValidateManifestResponse validate_manifest_api_v1_public_c2pa_validate_manifest_post(validate_manifest_request, authorization)
Validate C2PA-like manifest JSON (Public - Non-Cryptographic)

Validate a manifest JSON payload and (optionally) validate assertion payloads against provided JSON Schemas. This endpoint performs structural/schema validation only and does not verify cryptographic signatures.  Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**validate_manifest_request** | [**ValidateManifestRequest**](ValidateManifestRequest.md) |  | [required] |
**authorization** | Option<**String**> |  |  |

### Return type

[**models::ValidateManifestResponse**](ValidateManifestResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
