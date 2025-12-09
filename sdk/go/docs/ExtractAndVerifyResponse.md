# ExtractAndVerifyResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** | Whether embedding is valid | 
**VerifiedAt** | Pointer to **NullableTime** |  | [optional] 
**Content** | Pointer to [**NullableContentInfo**](ContentInfo.md) |  | [optional] 
**Document** | Pointer to [**NullableDocumentInfo**](DocumentInfo.md) |  | [optional] 
**MerkleProof** | Pointer to [**NullableMerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**C2pa** | Pointer to [**NullableC2PAInfo**](C2PAInfo.md) |  | [optional] 
**Licensing** | Pointer to [**NullableLicensingInfo**](LicensingInfo.md) |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewExtractAndVerifyResponse

`func NewExtractAndVerifyResponse(valid bool, ) *ExtractAndVerifyResponse`

NewExtractAndVerifyResponse instantiates a new ExtractAndVerifyResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewExtractAndVerifyResponseWithDefaults

`func NewExtractAndVerifyResponseWithDefaults() *ExtractAndVerifyResponse`

NewExtractAndVerifyResponseWithDefaults instantiates a new ExtractAndVerifyResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *ExtractAndVerifyResponse) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *ExtractAndVerifyResponse) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *ExtractAndVerifyResponse) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetVerifiedAt

`func (o *ExtractAndVerifyResponse) GetVerifiedAt() time.Time`

GetVerifiedAt returns the VerifiedAt field if non-nil, zero value otherwise.

### GetVerifiedAtOk

`func (o *ExtractAndVerifyResponse) GetVerifiedAtOk() (*time.Time, bool)`

GetVerifiedAtOk returns a tuple with the VerifiedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerifiedAt

`func (o *ExtractAndVerifyResponse) SetVerifiedAt(v time.Time)`

SetVerifiedAt sets VerifiedAt field to given value.

### HasVerifiedAt

`func (o *ExtractAndVerifyResponse) HasVerifiedAt() bool`

HasVerifiedAt returns a boolean if a field has been set.

### SetVerifiedAtNil

`func (o *ExtractAndVerifyResponse) SetVerifiedAtNil(b bool)`

 SetVerifiedAtNil sets the value for VerifiedAt to be an explicit nil

### UnsetVerifiedAt
`func (o *ExtractAndVerifyResponse) UnsetVerifiedAt()`

UnsetVerifiedAt ensures that no value is present for VerifiedAt, not even an explicit nil
### GetContent

`func (o *ExtractAndVerifyResponse) GetContent() ContentInfo`

GetContent returns the Content field if non-nil, zero value otherwise.

### GetContentOk

`func (o *ExtractAndVerifyResponse) GetContentOk() (*ContentInfo, bool)`

GetContentOk returns a tuple with the Content field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContent

`func (o *ExtractAndVerifyResponse) SetContent(v ContentInfo)`

SetContent sets Content field to given value.

### HasContent

`func (o *ExtractAndVerifyResponse) HasContent() bool`

HasContent returns a boolean if a field has been set.

### SetContentNil

`func (o *ExtractAndVerifyResponse) SetContentNil(b bool)`

 SetContentNil sets the value for Content to be an explicit nil

### UnsetContent
`func (o *ExtractAndVerifyResponse) UnsetContent()`

UnsetContent ensures that no value is present for Content, not even an explicit nil
### GetDocument

`func (o *ExtractAndVerifyResponse) GetDocument() DocumentInfo`

GetDocument returns the Document field if non-nil, zero value otherwise.

### GetDocumentOk

`func (o *ExtractAndVerifyResponse) GetDocumentOk() (*DocumentInfo, bool)`

GetDocumentOk returns a tuple with the Document field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocument

`func (o *ExtractAndVerifyResponse) SetDocument(v DocumentInfo)`

SetDocument sets Document field to given value.

### HasDocument

`func (o *ExtractAndVerifyResponse) HasDocument() bool`

HasDocument returns a boolean if a field has been set.

### SetDocumentNil

`func (o *ExtractAndVerifyResponse) SetDocumentNil(b bool)`

 SetDocumentNil sets the value for Document to be an explicit nil

### UnsetDocument
`func (o *ExtractAndVerifyResponse) UnsetDocument()`

UnsetDocument ensures that no value is present for Document, not even an explicit nil
### GetMerkleProof

`func (o *ExtractAndVerifyResponse) GetMerkleProof() MerkleProofInfo`

GetMerkleProof returns the MerkleProof field if non-nil, zero value otherwise.

### GetMerkleProofOk

`func (o *ExtractAndVerifyResponse) GetMerkleProofOk() (*MerkleProofInfo, bool)`

GetMerkleProofOk returns a tuple with the MerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleProof

`func (o *ExtractAndVerifyResponse) SetMerkleProof(v MerkleProofInfo)`

SetMerkleProof sets MerkleProof field to given value.

### HasMerkleProof

`func (o *ExtractAndVerifyResponse) HasMerkleProof() bool`

HasMerkleProof returns a boolean if a field has been set.

### SetMerkleProofNil

`func (o *ExtractAndVerifyResponse) SetMerkleProofNil(b bool)`

 SetMerkleProofNil sets the value for MerkleProof to be an explicit nil

### UnsetMerkleProof
`func (o *ExtractAndVerifyResponse) UnsetMerkleProof()`

UnsetMerkleProof ensures that no value is present for MerkleProof, not even an explicit nil
### GetC2pa

`func (o *ExtractAndVerifyResponse) GetC2pa() C2PAInfo`

GetC2pa returns the C2pa field if non-nil, zero value otherwise.

### GetC2paOk

`func (o *ExtractAndVerifyResponse) GetC2paOk() (*C2PAInfo, bool)`

GetC2paOk returns a tuple with the C2pa field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetC2pa

`func (o *ExtractAndVerifyResponse) SetC2pa(v C2PAInfo)`

SetC2pa sets C2pa field to given value.

### HasC2pa

`func (o *ExtractAndVerifyResponse) HasC2pa() bool`

HasC2pa returns a boolean if a field has been set.

### SetC2paNil

`func (o *ExtractAndVerifyResponse) SetC2paNil(b bool)`

 SetC2paNil sets the value for C2pa to be an explicit nil

### UnsetC2pa
`func (o *ExtractAndVerifyResponse) UnsetC2pa()`

UnsetC2pa ensures that no value is present for C2pa, not even an explicit nil
### GetLicensing

`func (o *ExtractAndVerifyResponse) GetLicensing() LicensingInfo`

GetLicensing returns the Licensing field if non-nil, zero value otherwise.

### GetLicensingOk

`func (o *ExtractAndVerifyResponse) GetLicensingOk() (*LicensingInfo, bool)`

GetLicensingOk returns a tuple with the Licensing field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicensing

`func (o *ExtractAndVerifyResponse) SetLicensing(v LicensingInfo)`

SetLicensing sets Licensing field to given value.

### HasLicensing

`func (o *ExtractAndVerifyResponse) HasLicensing() bool`

HasLicensing returns a boolean if a field has been set.

### SetLicensingNil

`func (o *ExtractAndVerifyResponse) SetLicensingNil(b bool)`

 SetLicensingNil sets the value for Licensing to be an explicit nil

### UnsetLicensing
`func (o *ExtractAndVerifyResponse) UnsetLicensing()`

UnsetLicensing ensures that no value is present for Licensing, not even an explicit nil
### GetMetadata

`func (o *ExtractAndVerifyResponse) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *ExtractAndVerifyResponse) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *ExtractAndVerifyResponse) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *ExtractAndVerifyResponse) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *ExtractAndVerifyResponse) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *ExtractAndVerifyResponse) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetError

`func (o *ExtractAndVerifyResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *ExtractAndVerifyResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *ExtractAndVerifyResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *ExtractAndVerifyResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *ExtractAndVerifyResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *ExtractAndVerifyResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


