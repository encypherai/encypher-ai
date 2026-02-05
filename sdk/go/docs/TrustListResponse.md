# TrustListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**TrustedCas** | Pointer to **[]string** |  | [optional] 
**TrustListUrl** | Pointer to **string** |  | [optional] [default to "https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem"]
**TrustListFingerprint** | Pointer to **NullableString** |  | [optional] 
**TrustListLoadedAt** | Pointer to **NullableString** |  | [optional] 
**TrustListSource** | Pointer to **NullableString** |  | [optional] 
**TrustListCount** | Pointer to **NullableString** |  | [optional] 

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

### GetTrustListFingerprint

`func (o *TrustListResponse) GetTrustListFingerprint() string`

GetTrustListFingerprint returns the TrustListFingerprint field if non-nil, zero value otherwise.

### GetTrustListFingerprintOk

`func (o *TrustListResponse) GetTrustListFingerprintOk() (*string, bool)`

GetTrustListFingerprintOk returns a tuple with the TrustListFingerprint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustListFingerprint

`func (o *TrustListResponse) SetTrustListFingerprint(v string)`

SetTrustListFingerprint sets TrustListFingerprint field to given value.

### HasTrustListFingerprint

`func (o *TrustListResponse) HasTrustListFingerprint() bool`

HasTrustListFingerprint returns a boolean if a field has been set.

### SetTrustListFingerprintNil

`func (o *TrustListResponse) SetTrustListFingerprintNil(b bool)`

 SetTrustListFingerprintNil sets the value for TrustListFingerprint to be an explicit nil

### UnsetTrustListFingerprint
`func (o *TrustListResponse) UnsetTrustListFingerprint()`

UnsetTrustListFingerprint ensures that no value is present for TrustListFingerprint, not even an explicit nil
### GetTrustListLoadedAt

`func (o *TrustListResponse) GetTrustListLoadedAt() string`

GetTrustListLoadedAt returns the TrustListLoadedAt field if non-nil, zero value otherwise.

### GetTrustListLoadedAtOk

`func (o *TrustListResponse) GetTrustListLoadedAtOk() (*string, bool)`

GetTrustListLoadedAtOk returns a tuple with the TrustListLoadedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustListLoadedAt

`func (o *TrustListResponse) SetTrustListLoadedAt(v string)`

SetTrustListLoadedAt sets TrustListLoadedAt field to given value.

### HasTrustListLoadedAt

`func (o *TrustListResponse) HasTrustListLoadedAt() bool`

HasTrustListLoadedAt returns a boolean if a field has been set.

### SetTrustListLoadedAtNil

`func (o *TrustListResponse) SetTrustListLoadedAtNil(b bool)`

 SetTrustListLoadedAtNil sets the value for TrustListLoadedAt to be an explicit nil

### UnsetTrustListLoadedAt
`func (o *TrustListResponse) UnsetTrustListLoadedAt()`

UnsetTrustListLoadedAt ensures that no value is present for TrustListLoadedAt, not even an explicit nil
### GetTrustListSource

`func (o *TrustListResponse) GetTrustListSource() string`

GetTrustListSource returns the TrustListSource field if non-nil, zero value otherwise.

### GetTrustListSourceOk

`func (o *TrustListResponse) GetTrustListSourceOk() (*string, bool)`

GetTrustListSourceOk returns a tuple with the TrustListSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustListSource

`func (o *TrustListResponse) SetTrustListSource(v string)`

SetTrustListSource sets TrustListSource field to given value.

### HasTrustListSource

`func (o *TrustListResponse) HasTrustListSource() bool`

HasTrustListSource returns a boolean if a field has been set.

### SetTrustListSourceNil

`func (o *TrustListResponse) SetTrustListSourceNil(b bool)`

 SetTrustListSourceNil sets the value for TrustListSource to be an explicit nil

### UnsetTrustListSource
`func (o *TrustListResponse) UnsetTrustListSource()`

UnsetTrustListSource ensures that no value is present for TrustListSource, not even an explicit nil
### GetTrustListCount

`func (o *TrustListResponse) GetTrustListCount() string`

GetTrustListCount returns the TrustListCount field if non-nil, zero value otherwise.

### GetTrustListCountOk

`func (o *TrustListResponse) GetTrustListCountOk() (*string, bool)`

GetTrustListCountOk returns a tuple with the TrustListCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustListCount

`func (o *TrustListResponse) SetTrustListCount(v string)`

SetTrustListCount sets TrustListCount field to given value.

### HasTrustListCount

`func (o *TrustListResponse) HasTrustListCount() bool`

HasTrustListCount returns a boolean if a field has been set.

### SetTrustListCountNil

`func (o *TrustListResponse) SetTrustListCountNil(b bool)`

 SetTrustListCountNil sets the value for TrustListCount to be an explicit nil

### UnsetTrustListCount
`func (o *TrustListResponse) UnsetTrustListCount()`

UnsetTrustListCount ensures that no value is present for TrustListCount, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


