# TrustListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**TrustedCas** | Pointer to **[]string** |  | [optional] 
**TrustListUrl** | Pointer to **string** |  | [optional] [default to "https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem"]

## Methods

### NewTrustListResponse

`func NewTrustListResponse() *TrustListResponse`

NewTrustListResponse instantiates a new TrustListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTrustListResponseWithDefaults

`func NewTrustListResponseWithDefaults() *TrustListResponse`

NewTrustListResponseWithDefaults instantiates a new TrustListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *TrustListResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *TrustListResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *TrustListResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *TrustListResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetTrustedCas

`func (o *TrustListResponse) GetTrustedCas() []string`

GetTrustedCas returns the TrustedCas field if non-nil, zero value otherwise.

### GetTrustedCasOk

`func (o *TrustListResponse) GetTrustedCasOk() (*[]string, bool)`

GetTrustedCasOk returns a tuple with the TrustedCas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustedCas

`func (o *TrustListResponse) SetTrustedCas(v []string)`

SetTrustedCas sets TrustedCas field to given value.

### HasTrustedCas

`func (o *TrustListResponse) HasTrustedCas() bool`

HasTrustedCas returns a boolean if a field has been set.

### GetTrustListUrl

`func (o *TrustListResponse) GetTrustListUrl() string`

GetTrustListUrl returns the TrustListUrl field if non-nil, zero value otherwise.

### GetTrustListUrlOk

`func (o *TrustListResponse) GetTrustListUrlOk() (*string, bool)`

GetTrustListUrlOk returns a tuple with the TrustListUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustListUrl

`func (o *TrustListResponse) SetTrustListUrl(v string)`

SetTrustListUrl sets TrustListUrl field to given value.

### HasTrustListUrl

`func (o *TrustListResponse) HasTrustListUrl() bool`

HasTrustListUrl returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


