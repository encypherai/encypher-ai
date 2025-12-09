# VerifyEmbeddingResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** | Whether embedding is valid | 
**RefId** | **string** | Reference ID | 
**VerifiedAt** | Pointer to **NullableTime** |  | [optional] 
**Content** | Pointer to [**NullableContentInfo**](ContentInfo.md) |  | [optional] 
**Document** | Pointer to [**NullableDocumentInfo**](DocumentInfo.md) |  | [optional] 
**MerkleProof** | Pointer to [**NullableMerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**C2pa** | Pointer to [**NullableC2PAInfo**](C2PAInfo.md) |  | [optional] 
**Licensing** | Pointer to [**NullableLicensingInfo**](LicensingInfo.md) |  | [optional] 
**VerificationUrl** | Pointer to **NullableString** |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewVerifyEmbeddingResponse

`func NewVerifyEmbeddingResponse(valid bool, refId string, ) *VerifyEmbeddingResponse`

NewVerifyEmbeddingResponse instantiates a new VerifyEmbeddingResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyEmbeddingResponseWithDefaults

`func NewVerifyEmbeddingResponseWithDefaults() *VerifyEmbeddingResponse`

NewVerifyEmbeddingResponseWithDefaults instantiates a new VerifyEmbeddingResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *VerifyEmbeddingResponse) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *VerifyEmbeddingResponse) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *VerifyEmbeddingResponse) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetRefId

`func (o *VerifyEmbeddingResponse) GetRefId() string`

GetRefId returns the RefId field if non-nil, zero value otherwise.

### GetRefIdOk

`func (o *VerifyEmbeddingResponse) GetRefIdOk() (*string, bool)`

GetRefIdOk returns a tuple with the RefId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRefId

`func (o *VerifyEmbeddingResponse) SetRefId(v string)`

SetRefId sets RefId field to given value.


### GetVerifiedAt

`func (o *VerifyEmbeddingResponse) GetVerifiedAt() time.Time`

GetVerifiedAt returns the VerifiedAt field if non-nil, zero value otherwise.

### GetVerifiedAtOk

`func (o *VerifyEmbeddingResponse) GetVerifiedAtOk() (*time.Time, bool)`

GetVerifiedAtOk returns a tuple with the VerifiedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerifiedAt

`func (o *VerifyEmbeddingResponse) SetVerifiedAt(v time.Time)`

SetVerifiedAt sets VerifiedAt field to given value.

### HasVerifiedAt

`func (o *VerifyEmbeddingResponse) HasVerifiedAt() bool`

HasVerifiedAt returns a boolean if a field has been set.

### SetVerifiedAtNil

`func (o *VerifyEmbeddingResponse) SetVerifiedAtNil(b bool)`

 SetVerifiedAtNil sets the value for VerifiedAt to be an explicit nil

### UnsetVerifiedAt
`func (o *VerifyEmbeddingResponse) UnsetVerifiedAt()`

UnsetVerifiedAt ensures that no value is present for VerifiedAt, not even an explicit nil
### GetContent

`func (o *VerifyEmbeddingResponse) GetContent() ContentInfo`

GetContent returns the Content field if non-nil, zero value otherwise.

### GetContentOk

`func (o *VerifyEmbeddingResponse) GetContentOk() (*ContentInfo, bool)`

GetContentOk returns a tuple with the Content field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContent

`func (o *VerifyEmbeddingResponse) SetContent(v ContentInfo)`

SetContent sets Content field to given value.

### HasContent

`func (o *VerifyEmbeddingResponse) HasContent() bool`

HasContent returns a boolean if a field has been set.

### SetContentNil

`func (o *VerifyEmbeddingResponse) SetContentNil(b bool)`

 SetContentNil sets the value for Content to be an explicit nil

### UnsetContent
`func (o *VerifyEmbeddingResponse) UnsetContent()`

UnsetContent ensures that no value is present for Content, not even an explicit nil
### GetDocument

`func (o *VerifyEmbeddingResponse) GetDocument() DocumentInfo`

GetDocument returns the Document field if non-nil, zero value otherwise.

### GetDocumentOk

`func (o *VerifyEmbeddingResponse) GetDocumentOk() (*DocumentInfo, bool)`

GetDocumentOk returns a tuple with the Document field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocument

`func (o *VerifyEmbeddingResponse) SetDocument(v DocumentInfo)`

SetDocument sets Document field to given value.

### HasDocument

`func (o *VerifyEmbeddingResponse) HasDocument() bool`

HasDocument returns a boolean if a field has been set.

### SetDocumentNil

`func (o *VerifyEmbeddingResponse) SetDocumentNil(b bool)`

 SetDocumentNil sets the value for Document to be an explicit nil

### UnsetDocument
`func (o *VerifyEmbeddingResponse) UnsetDocument()`

UnsetDocument ensures that no value is present for Document, not even an explicit nil
### GetMerkleProof

`func (o *VerifyEmbeddingResponse) GetMerkleProof() MerkleProofInfo`

GetMerkleProof returns the MerkleProof field if non-nil, zero value otherwise.

### GetMerkleProofOk

`func (o *VerifyEmbeddingResponse) GetMerkleProofOk() (*MerkleProofInfo, bool)`

GetMerkleProofOk returns a tuple with the MerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleProof

`func (o *VerifyEmbeddingResponse) SetMerkleProof(v MerkleProofInfo)`

SetMerkleProof sets MerkleProof field to given value.

### HasMerkleProof

`func (o *VerifyEmbeddingResponse) HasMerkleProof() bool`

HasMerkleProof returns a boolean if a field has been set.

### SetMerkleProofNil

`func (o *VerifyEmbeddingResponse) SetMerkleProofNil(b bool)`

 SetMerkleProofNil sets the value for MerkleProof to be an explicit nil

### UnsetMerkleProof
`func (o *VerifyEmbeddingResponse) UnsetMerkleProof()`

UnsetMerkleProof ensures that no value is present for MerkleProof, not even an explicit nil
### GetC2pa

`func (o *VerifyEmbeddingResponse) GetC2pa() C2PAInfo`

GetC2pa returns the C2pa field if non-nil, zero value otherwise.

### GetC2paOk

`func (o *VerifyEmbeddingResponse) GetC2paOk() (*C2PAInfo, bool)`

GetC2paOk returns a tuple with the C2pa field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetC2pa

`func (o *VerifyEmbeddingResponse) SetC2pa(v C2PAInfo)`

SetC2pa sets C2pa field to given value.

### HasC2pa

`func (o *VerifyEmbeddingResponse) HasC2pa() bool`

HasC2pa returns a boolean if a field has been set.

### SetC2paNil

`func (o *VerifyEmbeddingResponse) SetC2paNil(b bool)`

 SetC2paNil sets the value for C2pa to be an explicit nil

### UnsetC2pa
`func (o *VerifyEmbeddingResponse) UnsetC2pa()`

UnsetC2pa ensures that no value is present for C2pa, not even an explicit nil
### GetLicensing

`func (o *VerifyEmbeddingResponse) GetLicensing() LicensingInfo`

GetLicensing returns the Licensing field if non-nil, zero value otherwise.

### GetLicensingOk

`func (o *VerifyEmbeddingResponse) GetLicensingOk() (*LicensingInfo, bool)`

GetLicensingOk returns a tuple with the Licensing field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicensing

`func (o *VerifyEmbeddingResponse) SetLicensing(v LicensingInfo)`

SetLicensing sets Licensing field to given value.

### HasLicensing

`func (o *VerifyEmbeddingResponse) HasLicensing() bool`

HasLicensing returns a boolean if a field has been set.

### SetLicensingNil

`func (o *VerifyEmbeddingResponse) SetLicensingNil(b bool)`

 SetLicensingNil sets the value for Licensing to be an explicit nil

### UnsetLicensing
`func (o *VerifyEmbeddingResponse) UnsetLicensing()`

UnsetLicensing ensures that no value is present for Licensing, not even an explicit nil
### GetVerificationUrl

`func (o *VerifyEmbeddingResponse) GetVerificationUrl() string`

GetVerificationUrl returns the VerificationUrl field if non-nil, zero value otherwise.

### GetVerificationUrlOk

`func (o *VerifyEmbeddingResponse) GetVerificationUrlOk() (*string, bool)`

GetVerificationUrlOk returns a tuple with the VerificationUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationUrl

`func (o *VerifyEmbeddingResponse) SetVerificationUrl(v string)`

SetVerificationUrl sets VerificationUrl field to given value.

### HasVerificationUrl

`func (o *VerifyEmbeddingResponse) HasVerificationUrl() bool`

HasVerificationUrl returns a boolean if a field has been set.

### SetVerificationUrlNil

`func (o *VerifyEmbeddingResponse) SetVerificationUrlNil(b bool)`

 SetVerificationUrlNil sets the value for VerificationUrl to be an explicit nil

### UnsetVerificationUrl
`func (o *VerifyEmbeddingResponse) UnsetVerificationUrl()`

UnsetVerificationUrl ensures that no value is present for VerificationUrl, not even an explicit nil
### GetError

`func (o *VerifyEmbeddingResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *VerifyEmbeddingResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *VerifyEmbeddingResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *VerifyEmbeddingResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *VerifyEmbeddingResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *VerifyEmbeddingResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


