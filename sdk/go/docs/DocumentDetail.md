# DocumentDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** |  | 
**Title** | Pointer to **NullableString** |  | [optional] 
**DocumentType** | Pointer to **NullableString** |  | [optional] 
**Status** | Pointer to **string** |  | [optional] [default to "active"]
**SignedAt** | **string** |  | 
**VerificationUrl** | **string** |  | 
**WordCount** | Pointer to **NullableInt32** |  | [optional] 
**Url** | Pointer to **NullableString** |  | [optional] 
**SignerId** | Pointer to **NullableString** |  | [optional] 
**RevokedAt** | Pointer to **NullableString** |  | [optional] 
**RevokedReason** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewDocumentDetail

`func NewDocumentDetail(documentId string, signedAt string, verificationUrl string, ) *DocumentDetail`

NewDocumentDetail instantiates a new DocumentDetail object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentDetailWithDefaults

`func NewDocumentDetailWithDefaults() *DocumentDetail`

NewDocumentDetailWithDefaults instantiates a new DocumentDetail object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *DocumentDetail) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *DocumentDetail) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *DocumentDetail) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetTitle

`func (o *DocumentDetail) GetTitle() string`

GetTitle returns the Title field if non-nil, zero value otherwise.

### GetTitleOk

`func (o *DocumentDetail) GetTitleOk() (*string, bool)`

GetTitleOk returns a tuple with the Title field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTitle

`func (o *DocumentDetail) SetTitle(v string)`

SetTitle sets Title field to given value.

### HasTitle

`func (o *DocumentDetail) HasTitle() bool`

HasTitle returns a boolean if a field has been set.

### SetTitleNil

`func (o *DocumentDetail) SetTitleNil(b bool)`

 SetTitleNil sets the value for Title to be an explicit nil

### UnsetTitle
`func (o *DocumentDetail) UnsetTitle()`

UnsetTitle ensures that no value is present for Title, not even an explicit nil
### GetDocumentType

`func (o *DocumentDetail) GetDocumentType() string`

GetDocumentType returns the DocumentType field if non-nil, zero value otherwise.

### GetDocumentTypeOk

`func (o *DocumentDetail) GetDocumentTypeOk() (*string, bool)`

GetDocumentTypeOk returns a tuple with the DocumentType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentType

`func (o *DocumentDetail) SetDocumentType(v string)`

SetDocumentType sets DocumentType field to given value.

### HasDocumentType

`func (o *DocumentDetail) HasDocumentType() bool`

HasDocumentType returns a boolean if a field has been set.

### SetDocumentTypeNil

`func (o *DocumentDetail) SetDocumentTypeNil(b bool)`

 SetDocumentTypeNil sets the value for DocumentType to be an explicit nil

### UnsetDocumentType
`func (o *DocumentDetail) UnsetDocumentType()`

UnsetDocumentType ensures that no value is present for DocumentType, not even an explicit nil
### GetStatus

`func (o *DocumentDetail) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *DocumentDetail) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *DocumentDetail) SetStatus(v string)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *DocumentDetail) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### GetSignedAt

`func (o *DocumentDetail) GetSignedAt() string`

GetSignedAt returns the SignedAt field if non-nil, zero value otherwise.

### GetSignedAtOk

`func (o *DocumentDetail) GetSignedAtOk() (*string, bool)`

GetSignedAtOk returns a tuple with the SignedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedAt

`func (o *DocumentDetail) SetSignedAt(v string)`

SetSignedAt sets SignedAt field to given value.


### GetVerificationUrl

`func (o *DocumentDetail) GetVerificationUrl() string`

GetVerificationUrl returns the VerificationUrl field if non-nil, zero value otherwise.

### GetVerificationUrlOk

`func (o *DocumentDetail) GetVerificationUrlOk() (*string, bool)`

GetVerificationUrlOk returns a tuple with the VerificationUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationUrl

`func (o *DocumentDetail) SetVerificationUrl(v string)`

SetVerificationUrl sets VerificationUrl field to given value.


### GetWordCount

`func (o *DocumentDetail) GetWordCount() int32`

GetWordCount returns the WordCount field if non-nil, zero value otherwise.

### GetWordCountOk

`func (o *DocumentDetail) GetWordCountOk() (*int32, bool)`

GetWordCountOk returns a tuple with the WordCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWordCount

`func (o *DocumentDetail) SetWordCount(v int32)`

SetWordCount sets WordCount field to given value.

### HasWordCount

`func (o *DocumentDetail) HasWordCount() bool`

HasWordCount returns a boolean if a field has been set.

### SetWordCountNil

`func (o *DocumentDetail) SetWordCountNil(b bool)`

 SetWordCountNil sets the value for WordCount to be an explicit nil

### UnsetWordCount
`func (o *DocumentDetail) UnsetWordCount()`

UnsetWordCount ensures that no value is present for WordCount, not even an explicit nil
### GetUrl

`func (o *DocumentDetail) GetUrl() string`

GetUrl returns the Url field if non-nil, zero value otherwise.

### GetUrlOk

`func (o *DocumentDetail) GetUrlOk() (*string, bool)`

GetUrlOk returns a tuple with the Url field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUrl

`func (o *DocumentDetail) SetUrl(v string)`

SetUrl sets Url field to given value.

### HasUrl

`func (o *DocumentDetail) HasUrl() bool`

HasUrl returns a boolean if a field has been set.

### SetUrlNil

`func (o *DocumentDetail) SetUrlNil(b bool)`

 SetUrlNil sets the value for Url to be an explicit nil

### UnsetUrl
`func (o *DocumentDetail) UnsetUrl()`

UnsetUrl ensures that no value is present for Url, not even an explicit nil
### GetSignerId

`func (o *DocumentDetail) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *DocumentDetail) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *DocumentDetail) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.

### HasSignerId

`func (o *DocumentDetail) HasSignerId() bool`

HasSignerId returns a boolean if a field has been set.

### SetSignerIdNil

`func (o *DocumentDetail) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *DocumentDetail) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetRevokedAt

`func (o *DocumentDetail) GetRevokedAt() string`

GetRevokedAt returns the RevokedAt field if non-nil, zero value otherwise.

### GetRevokedAtOk

`func (o *DocumentDetail) GetRevokedAtOk() (*string, bool)`

GetRevokedAtOk returns a tuple with the RevokedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevokedAt

`func (o *DocumentDetail) SetRevokedAt(v string)`

SetRevokedAt sets RevokedAt field to given value.

### HasRevokedAt

`func (o *DocumentDetail) HasRevokedAt() bool`

HasRevokedAt returns a boolean if a field has been set.

### SetRevokedAtNil

`func (o *DocumentDetail) SetRevokedAtNil(b bool)`

 SetRevokedAtNil sets the value for RevokedAt to be an explicit nil

### UnsetRevokedAt
`func (o *DocumentDetail) UnsetRevokedAt()`

UnsetRevokedAt ensures that no value is present for RevokedAt, not even an explicit nil
### GetRevokedReason

`func (o *DocumentDetail) GetRevokedReason() string`

GetRevokedReason returns the RevokedReason field if non-nil, zero value otherwise.

### GetRevokedReasonOk

`func (o *DocumentDetail) GetRevokedReasonOk() (*string, bool)`

GetRevokedReasonOk returns a tuple with the RevokedReason field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevokedReason

`func (o *DocumentDetail) SetRevokedReason(v string)`

SetRevokedReason sets RevokedReason field to given value.

### HasRevokedReason

`func (o *DocumentDetail) HasRevokedReason() bool`

HasRevokedReason returns a boolean if a field has been set.

### SetRevokedReasonNil

`func (o *DocumentDetail) SetRevokedReasonNil(b bool)`

 SetRevokedReasonNil sets the value for RevokedReason to be an explicit nil

### UnsetRevokedReason
`func (o *DocumentDetail) UnsetRevokedReason()`

UnsetRevokedReason ensures that no value is present for RevokedReason, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


