# \LicensingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_agreement_api_v1_licensing_agreements_post**](LicensingApi.md#create_agreement_api_v1_licensing_agreements_post) | **POST** /api/v1/licensing/agreements | Create Agreement
[**create_agreement_api_v1_licensing_agreements_post_0**](LicensingApi.md#create_agreement_api_v1_licensing_agreements_post_0) | **POST** /api/v1/licensing/agreements | Create Agreement
[**create_revenue_distribution_api_v1_licensing_distributions_post**](LicensingApi.md#create_revenue_distribution_api_v1_licensing_distributions_post) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
[**create_revenue_distribution_api_v1_licensing_distributions_post_0**](LicensingApi.md#create_revenue_distribution_api_v1_licensing_distributions_post_0) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
[**get_agreement_api_v1_licensing_agreements_agreement_id_get**](LicensingApi.md#get_agreement_api_v1_licensing_agreements_agreement_id_get) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**get_agreement_api_v1_licensing_agreements_agreement_id_get_0**](LicensingApi.md#get_agreement_api_v1_licensing_agreements_agreement_id_get_0) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
[**get_distribution_api_v1_licensing_distributions_distribution_id_get**](LicensingApi.md#get_distribution_api_v1_licensing_distributions_distribution_id_get) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**get_distribution_api_v1_licensing_distributions_distribution_id_get_0**](LicensingApi.md#get_distribution_api_v1_licensing_distributions_distribution_id_get_0) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
[**list_agreements_api_v1_licensing_agreements_get**](LicensingApi.md#list_agreements_api_v1_licensing_agreements_get) | **GET** /api/v1/licensing/agreements | List Agreements
[**list_agreements_api_v1_licensing_agreements_get_0**](LicensingApi.md#list_agreements_api_v1_licensing_agreements_get_0) | **GET** /api/v1/licensing/agreements | List Agreements
[**list_available_content_api_v1_licensing_content_get**](LicensingApi.md#list_available_content_api_v1_licensing_content_get) | **GET** /api/v1/licensing/content | List Available Content
[**list_available_content_api_v1_licensing_content_get_0**](LicensingApi.md#list_available_content_api_v1_licensing_content_get_0) | **GET** /api/v1/licensing/content | List Available Content
[**list_distributions_api_v1_licensing_distributions_get**](LicensingApi.md#list_distributions_api_v1_licensing_distributions_get) | **GET** /api/v1/licensing/distributions | List Distributions
[**list_distributions_api_v1_licensing_distributions_get_0**](LicensingApi.md#list_distributions_api_v1_licensing_distributions_get_0) | **GET** /api/v1/licensing/distributions | List Distributions
[**process_payouts_api_v1_licensing_payouts_post**](LicensingApi.md#process_payouts_api_v1_licensing_payouts_post) | **POST** /api/v1/licensing/payouts | Process Payouts
[**process_payouts_api_v1_licensing_payouts_post_0**](LicensingApi.md#process_payouts_api_v1_licensing_payouts_post_0) | **POST** /api/v1/licensing/payouts | Process Payouts
[**terminate_agreement_api_v1_licensing_agreements_agreement_id_delete**](LicensingApi.md#terminate_agreement_api_v1_licensing_agreements_agreement_id_delete) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0**](LicensingApi.md#terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
[**track_content_access_api_v1_licensing_track_access_post**](LicensingApi.md#track_content_access_api_v1_licensing_track_access_post) | **POST** /api/v1/licensing/track-access | Track Content Access
[**track_content_access_api_v1_licensing_track_access_post_0**](LicensingApi.md#track_content_access_api_v1_licensing_track_access_post_0) | **POST** /api/v1/licensing/track-access | Track Content Access
[**update_agreement_api_v1_licensing_agreements_agreement_id_patch**](LicensingApi.md#update_agreement_api_v1_licensing_agreements_agreement_id_patch) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement
[**update_agreement_api_v1_licensing_agreements_agreement_id_patch_0**](LicensingApi.md#update_agreement_api_v1_licensing_agreements_agreement_id_patch_0) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement



## create_agreement_api_v1_licensing_agreements_post

> models::LicensingAgreementCreateResponse create_agreement_api_v1_licensing_agreements_post(licensing_agreement_create)
Create Agreement

Create a new licensing agreement with an AI company.  **Admin only** - Creates agreement and generates API key for AI company.  Returns:     Agreement details including the API key (only shown once)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**licensing_agreement_create** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md) |  | [required] |

### Return type

[**models::LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_agreement_api_v1_licensing_agreements_post_0

> models::LicensingAgreementCreateResponse create_agreement_api_v1_licensing_agreements_post_0(licensing_agreement_create)
Create Agreement

Create a new licensing agreement with an AI company.  **Admin only** - Creates agreement and generates API key for AI company.  Returns:     Agreement details including the API key (only shown once)

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**licensing_agreement_create** | [**LicensingAgreementCreate**](LicensingAgreementCreate.md) |  | [required] |

### Return type

[**models::LicensingAgreementCreateResponse**](LicensingAgreementCreateResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_revenue_distribution_api_v1_licensing_distributions_post

> models::RevenueDistributionResponse create_revenue_distribution_api_v1_licensing_distributions_post(revenue_distribution_create)
Create Revenue Distribution

Create revenue distribution for a period.  **Admin only** - Calculates and creates revenue distribution based on content access during the specified period. Implements 70/30 split.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**revenue_distribution_create** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md) |  | [required] |

### Return type

[**models::RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## create_revenue_distribution_api_v1_licensing_distributions_post_0

> models::RevenueDistributionResponse create_revenue_distribution_api_v1_licensing_distributions_post_0(revenue_distribution_create)
Create Revenue Distribution

Create revenue distribution for a period.  **Admin only** - Calculates and creates revenue distribution based on content access during the specified period. Implements 70/30 split.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**revenue_distribution_create** | [**RevenueDistributionCreate**](RevenueDistributionCreate.md) |  | [required] |

### Return type

[**models::RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_agreement_api_v1_licensing_agreements_agreement_id_get

> models::LicensingAgreementResponse get_agreement_api_v1_licensing_agreements_agreement_id_get(agreement_id)
Get Agreement

Get details of a specific licensing agreement.  **Admin only**

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_agreement_api_v1_licensing_agreements_agreement_id_get_0

> models::LicensingAgreementResponse get_agreement_api_v1_licensing_agreements_agreement_id_get_0(agreement_id)
Get Agreement

Get details of a specific licensing agreement.  **Admin only**

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_distribution_api_v1_licensing_distributions_distribution_id_get

> models::RevenueDistributionResponse get_distribution_api_v1_licensing_distributions_distribution_id_get(distribution_id)
Get Distribution

Get details of a revenue distribution.  **Admin only** - Includes breakdown of member revenues.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**distribution_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## get_distribution_api_v1_licensing_distributions_distribution_id_get_0

> models::RevenueDistributionResponse get_distribution_api_v1_licensing_distributions_distribution_id_get_0(distribution_id)
Get Distribution

Get details of a revenue distribution.  **Admin only** - Includes breakdown of member revenues.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**distribution_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::RevenueDistributionResponse**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_agreements_api_v1_licensing_agreements_get

> Vec<models::LicensingAgreementResponse> list_agreements_api_v1_licensing_agreements_get(status, limit, offset)
List Agreements

List all licensing agreements.  **Admin only** - Returns all agreements with optional filtering.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**status** | Option<[**AgreementStatus**](.md)> | Filter by status |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**Vec<models::LicensingAgreementResponse>**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_agreements_api_v1_licensing_agreements_get_0

> Vec<models::LicensingAgreementResponse> list_agreements_api_v1_licensing_agreements_get_0(status, limit, offset)
List Agreements

List all licensing agreements.  **Admin only** - Returns all agreements with optional filtering.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**status** | Option<[**AgreementStatus**](.md)> | Filter by status |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**Vec<models::LicensingAgreementResponse>**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_available_content_api_v1_licensing_content_get

> models::ContentListResponse list_available_content_api_v1_licensing_content_get(content_type, min_word_count, limit, offset)
List Available Content

List available content for licensed AI company.  **Requires AI company API key** - Returns content metadata that matches the terms of active licensing agreements.  Headers:     Authorization: Bearer lic_abc123...

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**content_type** | Option<**String**> | Filter by content type |  |
**min_word_count** | Option<**i32**> | Minimum word count |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**models::ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_available_content_api_v1_licensing_content_get_0

> models::ContentListResponse list_available_content_api_v1_licensing_content_get_0(content_type, min_word_count, limit, offset)
List Available Content

List available content for licensed AI company.  **Requires AI company API key** - Returns content metadata that matches the terms of active licensing agreements.  Headers:     Authorization: Bearer lic_abc123...

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**content_type** | Option<**String**> | Filter by content type |  |
**min_word_count** | Option<**i32**> | Minimum word count |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**models::ContentListResponse**](ContentListResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_distributions_api_v1_licensing_distributions_get

> Vec<models::RevenueDistributionResponse> list_distributions_api_v1_licensing_distributions_get(agreement_id, status, limit, offset)
List Distributions

List revenue distributions.  **Admin only** - Returns all distributions with optional filtering.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | Option<**uuid::Uuid**> | Filter by agreement |  |
**status** | Option<[**DistributionStatus**](.md)> | Filter by status |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**Vec<models::RevenueDistributionResponse>**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## list_distributions_api_v1_licensing_distributions_get_0

> Vec<models::RevenueDistributionResponse> list_distributions_api_v1_licensing_distributions_get_0(agreement_id, status, limit, offset)
List Distributions

List revenue distributions.  **Admin only** - Returns all distributions with optional filtering.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | Option<**uuid::Uuid**> | Filter by agreement |  |
**status** | Option<[**DistributionStatus**](.md)> | Filter by status |  |
**limit** | Option<**i32**> | Results per page |  |[default to 100]
**offset** | Option<**i32**> | Pagination offset |  |[default to 0]

### Return type

[**Vec<models::RevenueDistributionResponse>**](RevenueDistributionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## process_payouts_api_v1_licensing_payouts_post

> models::PayoutResponse process_payouts_api_v1_licensing_payouts_post(payout_create)
Process Payouts

Process payouts for a revenue distribution.  **Admin only** - Initiates payment processing for all members in a distribution.  Note: This is currently a simulation. In production, this would integrate with Stripe or other payment processors.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**payout_create** | [**PayoutCreate**](PayoutCreate.md) |  | [required] |

### Return type

[**models::PayoutResponse**](PayoutResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## process_payouts_api_v1_licensing_payouts_post_0

> models::PayoutResponse process_payouts_api_v1_licensing_payouts_post_0(payout_create)
Process Payouts

Process payouts for a revenue distribution.  **Admin only** - Initiates payment processing for all members in a distribution.  Note: This is currently a simulation. In production, this would integrate with Stripe or other payment processors.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**payout_create** | [**PayoutCreate**](PayoutCreate.md) |  | [required] |

### Return type

[**models::PayoutResponse**](PayoutResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## terminate_agreement_api_v1_licensing_agreements_agreement_id_delete

> models::SuccessResponse terminate_agreement_api_v1_licensing_agreements_agreement_id_delete(agreement_id)
Terminate Agreement

Terminate a licensing agreement.  **Admin only** - Sets agreement status to terminated.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0

> models::SuccessResponse terminate_agreement_api_v1_licensing_agreements_agreement_id_delete_0(agreement_id)
Terminate Agreement

Terminate a licensing agreement.  **Admin only** - Sets agreement status to terminated.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |

### Return type

[**models::SuccessResponse**](SuccessResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## track_content_access_api_v1_licensing_track_access_post

> models::ContentAccessLogResponse track_content_access_api_v1_licensing_track_access_post(content_access_track)
Track Content Access

Track content access by AI company.  **Requires AI company API key** - Logs when content is accessed for revenue attribution.  Headers:     Authorization: Bearer lic_abc123...

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**content_access_track** | [**ContentAccessTrack**](ContentAccessTrack.md) |  | [required] |

### Return type

[**models::ContentAccessLogResponse**](ContentAccessLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## track_content_access_api_v1_licensing_track_access_post_0

> models::ContentAccessLogResponse track_content_access_api_v1_licensing_track_access_post_0(content_access_track)
Track Content Access

Track content access by AI company.  **Requires AI company API key** - Logs when content is accessed for revenue attribution.  Headers:     Authorization: Bearer lic_abc123...

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**content_access_track** | [**ContentAccessTrack**](ContentAccessTrack.md) |  | [required] |

### Return type

[**models::ContentAccessLogResponse**](ContentAccessLogResponse.md)

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_agreement_api_v1_licensing_agreements_agreement_id_patch

> models::LicensingAgreementResponse update_agreement_api_v1_licensing_agreements_agreement_id_patch(agreement_id, licensing_agreement_update)
Update Agreement

Update a licensing agreement.  **Admin only** - Allows updating agreement terms and status.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |
**licensing_agreement_update** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md) |  | [required] |

### Return type

[**models::LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


## update_agreement_api_v1_licensing_agreements_agreement_id_patch_0

> models::LicensingAgreementResponse update_agreement_api_v1_licensing_agreements_agreement_id_patch_0(agreement_id, licensing_agreement_update)
Update Agreement

Update a licensing agreement.  **Admin only** - Allows updating agreement terms and status.

### Parameters


Name | Type | Description  | Required | Notes
------------- | ------------- | ------------- | ------------- | -------------
**agreement_id** | **uuid::Uuid** |  | [required] |
**licensing_agreement_update** | [**LicensingAgreementUpdate**](LicensingAgreementUpdate.md) |  | [required] |

### Return type

[**models::LicensingAgreementResponse**](LicensingAgreementResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

