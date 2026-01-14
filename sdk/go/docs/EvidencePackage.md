# EvidencePackage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**EvidenceId** | **string** | Unique evidence package ID | 
**GeneratedAt** | **time.Time** | When evidence was generated | 
**TargetTextHash** | **string** | Hash of target text | 
**TargetTextPreview** | **string** | Preview of target text (first 200 chars) | 
**AttributionFound** | **bool** | Whether attribution was found | 
**AttributionConfidence** | **float32** | Overall confidence score | 
**SourceDocumentId** | Pointer to **NullableString** |  | [optional] 
**SourceOrganizationId** | Pointer to **NullableString** |  | [optional] 
**SourceOrganizationName** | Pointer to **NullableString** |  | [optional] 
**MerkleRootHash** | Pointer to **NullableString** |  | [optional] 
**MerkleProof** | Pointer to [**[]MerkleProofItem**](MerkleProofItem.md) |  | [optional] 
**MerkleProofValid** | Pointer to **NullableBool** |  | [optional] 
**SignatureVerification** | Pointer to [**NullableSignatureVerification**](SignatureVerification.md) |  | [optional] 
**ContentMatches** | Pointer to [**[]ContentMatch**](ContentMatch.md) | List of matched content segments | [optional] 
**OriginalTimestamp** | Pointer to **NullableTime** |  | [optional] 
**TimestampVerified** | Pointer to **NullableBool** |  | [optional] 
**JsonExportUrl** | Pointer to **NullableString** |  | [optional] 
**PdfExportUrl** | Pointer to **NullableString** |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewEvidencePackage

`func NewEvidencePackage(evidenceId string, generatedAt time.Time, targetTextHash string, targetTextPreview string, attributionFound bool, attributionConfidence float32, ) *EvidencePackage`

NewEvidencePackage instantiates a new EvidencePackage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEvidencePackageWithDefaults

`func NewEvidencePackageWithDefaults() *EvidencePackage`

NewEvidencePackageWithDefaults instantiates a new EvidencePackage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEvidenceId

`func (o *EvidencePackage) GetEvidenceId() string`

GetEvidenceId returns the EvidenceId field if non-nil, zero value otherwise.

### GetEvidenceIdOk

`func (o *EvidencePackage) GetEvidenceIdOk() (*string, bool)`

GetEvidenceIdOk returns a tuple with the EvidenceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEvidenceId

`func (o *EvidencePackage) SetEvidenceId(v string)`

SetEvidenceId sets EvidenceId field to given value.


### GetGeneratedAt

`func (o *EvidencePackage) GetGeneratedAt() time.Time`

GetGeneratedAt returns the GeneratedAt field if non-nil, zero value otherwise.

### GetGeneratedAtOk

`func (o *EvidencePackage) GetGeneratedAtOk() (*time.Time, bool)`

GetGeneratedAtOk returns a tuple with the GeneratedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetGeneratedAt

`func (o *EvidencePackage) SetGeneratedAt(v time.Time)`

SetGeneratedAt sets GeneratedAt field to given value.


### GetTargetTextHash

`func (o *EvidencePackage) GetTargetTextHash() string`

GetTargetTextHash returns the TargetTextHash field if non-nil, zero value otherwise.

### GetTargetTextHashOk

`func (o *EvidencePackage) GetTargetTextHashOk() (*string, bool)`

GetTargetTextHashOk returns a tuple with the TargetTextHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetTextHash

`func (o *EvidencePackage) SetTargetTextHash(v string)`

SetTargetTextHash sets TargetTextHash field to given value.


### GetTargetTextPreview

`func (o *EvidencePackage) GetTargetTextPreview() string`

GetTargetTextPreview returns the TargetTextPreview field if non-nil, zero value otherwise.

### GetTargetTextPreviewOk

`func (o *EvidencePackage) GetTargetTextPreviewOk() (*string, bool)`

GetTargetTextPreviewOk returns a tuple with the TargetTextPreview field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetTextPreview

`func (o *EvidencePackage) SetTargetTextPreview(v string)`

SetTargetTextPreview sets TargetTextPreview field to given value.


### GetAttributionFound

`func (o *EvidencePackage) GetAttributionFound() bool`

GetAttributionFound returns the AttributionFound field if non-nil, zero value otherwise.

### GetAttributionFoundOk

`func (o *EvidencePackage) GetAttributionFoundOk() (*bool, bool)`

GetAttributionFoundOk returns a tuple with the AttributionFound field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAttributionFound

`func (o *EvidencePackage) SetAttributionFound(v bool)`

SetAttributionFound sets AttributionFound field to given value.


### GetAttributionConfidence

`func (o *EvidencePackage) GetAttributionConfidence() float32`

GetAttributionConfidence returns the AttributionConfidence field if non-nil, zero value otherwise.

### GetAttributionConfidenceOk

`func (o *EvidencePackage) GetAttributionConfidenceOk() (*float32, bool)`

GetAttributionConfidenceOk returns a tuple with the AttributionConfidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAttributionConfidence

`func (o *EvidencePackage) SetAttributionConfidence(v float32)`

SetAttributionConfidence sets AttributionConfidence field to given value.


### GetSourceDocumentId

`func (o *EvidencePackage) GetSourceDocumentId() string`

GetSourceDocumentId returns the SourceDocumentId field if non-nil, zero value otherwise.

### GetSourceDocumentIdOk

`func (o *EvidencePackage) GetSourceDocumentIdOk() (*string, bool)`

GetSourceDocumentIdOk returns a tuple with the SourceDocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceDocumentId

`func (o *EvidencePackage) SetSourceDocumentId(v string)`

SetSourceDocumentId sets SourceDocumentId field to given value.

### HasSourceDocumentId

`func (o *EvidencePackage) HasSourceDocumentId() bool`

HasSourceDocumentId returns a boolean if a field has been set.

### SetSourceDocumentIdNil

`func (o *EvidencePackage) SetSourceDocumentIdNil(b bool)`

 SetSourceDocumentIdNil sets the value for SourceDocumentId to be an explicit nil

### UnsetSourceDocumentId
`func (o *EvidencePackage) UnsetSourceDocumentId()`

UnsetSourceDocumentId ensures that no value is present for SourceDocumentId, not even an explicit nil
### GetSourceOrganizationId

`func (o *EvidencePackage) GetSourceOrganizationId() string`

GetSourceOrganizationId returns the SourceOrganizationId field if non-nil, zero value otherwise.

### GetSourceOrganizationIdOk

`func (o *EvidencePackage) GetSourceOrganizationIdOk() (*string, bool)`

GetSourceOrganizationIdOk returns a tuple with the SourceOrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceOrganizationId

`func (o *EvidencePackage) SetSourceOrganizationId(v string)`

SetSourceOrganizationId sets SourceOrganizationId field to given value.

### HasSourceOrganizationId

`func (o *EvidencePackage) HasSourceOrganizationId() bool`

HasSourceOrganizationId returns a boolean if a field has been set.

### SetSourceOrganizationIdNil

`func (o *EvidencePackage) SetSourceOrganizationIdNil(b bool)`

 SetSourceOrganizationIdNil sets the value for SourceOrganizationId to be an explicit nil

### UnsetSourceOrganizationId
`func (o *EvidencePackage) UnsetSourceOrganizationId()`

UnsetSourceOrganizationId ensures that no value is present for SourceOrganizationId, not even an explicit nil
### GetSourceOrganizationName

`func (o *EvidencePackage) GetSourceOrganizationName() string`

GetSourceOrganizationName returns the SourceOrganizationName field if non-nil, zero value otherwise.

### GetSourceOrganizationNameOk

`func (o *EvidencePackage) GetSourceOrganizationNameOk() (*string, bool)`

GetSourceOrganizationNameOk returns a tuple with the SourceOrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceOrganizationName

`func (o *EvidencePackage) SetSourceOrganizationName(v string)`

SetSourceOrganizationName sets SourceOrganizationName field to given value.

### HasSourceOrganizationName

`func (o *EvidencePackage) HasSourceOrganizationName() bool`

HasSourceOrganizationName returns a boolean if a field has been set.

### SetSourceOrganizationNameNil

`func (o *EvidencePackage) SetSourceOrganizationNameNil(b bool)`

 SetSourceOrganizationNameNil sets the value for SourceOrganizationName to be an explicit nil

### UnsetSourceOrganizationName
`func (o *EvidencePackage) UnsetSourceOrganizationName()`

UnsetSourceOrganizationName ensures that no value is present for SourceOrganizationName, not even an explicit nil
### GetMerkleRootHash

`func (o *EvidencePackage) GetMerkleRootHash() string`

GetMerkleRootHash returns the MerkleRootHash field if non-nil, zero value otherwise.

### GetMerkleRootHashOk

`func (o *EvidencePackage) GetMerkleRootHashOk() (*string, bool)`

GetMerkleRootHashOk returns a tuple with the MerkleRootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleRootHash

`func (o *EvidencePackage) SetMerkleRootHash(v string)`

SetMerkleRootHash sets MerkleRootHash field to given value.

### HasMerkleRootHash

`func (o *EvidencePackage) HasMerkleRootHash() bool`

HasMerkleRootHash returns a boolean if a field has been set.

### SetMerkleRootHashNil

`func (o *EvidencePackage) SetMerkleRootHashNil(b bool)`

 SetMerkleRootHashNil sets the value for MerkleRootHash to be an explicit nil

### UnsetMerkleRootHash
`func (o *EvidencePackage) UnsetMerkleRootHash()`

UnsetMerkleRootHash ensures that no value is present for MerkleRootHash, not even an explicit nil
### GetMerkleProof

`func (o *EvidencePackage) GetMerkleProof() []MerkleProofItem`

GetMerkleProof returns the MerkleProof field if non-nil, zero value otherwise.

### GetMerkleProofOk

`func (o *EvidencePackage) GetMerkleProofOk() (*[]MerkleProofItem, bool)`

GetMerkleProofOk returns a tuple with the MerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleProof

`func (o *EvidencePackage) SetMerkleProof(v []MerkleProofItem)`

SetMerkleProof sets MerkleProof field to given value.

### HasMerkleProof

`func (o *EvidencePackage) HasMerkleProof() bool`

HasMerkleProof returns a boolean if a field has been set.

### SetMerkleProofNil

`func (o *EvidencePackage) SetMerkleProofNil(b bool)`

 SetMerkleProofNil sets the value for MerkleProof to be an explicit nil

### UnsetMerkleProof
`func (o *EvidencePackage) UnsetMerkleProof()`

UnsetMerkleProof ensures that no value is present for MerkleProof, not even an explicit nil
### GetMerkleProofValid

`func (o *EvidencePackage) GetMerkleProofValid() bool`

GetMerkleProofValid returns the MerkleProofValid field if non-nil, zero value otherwise.

### GetMerkleProofValidOk

`func (o *EvidencePackage) GetMerkleProofValidOk() (*bool, bool)`

GetMerkleProofValidOk returns a tuple with the MerkleProofValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleProofValid

`func (o *EvidencePackage) SetMerkleProofValid(v bool)`

SetMerkleProofValid sets MerkleProofValid field to given value.

### HasMerkleProofValid

`func (o *EvidencePackage) HasMerkleProofValid() bool`

HasMerkleProofValid returns a boolean if a field has been set.

### SetMerkleProofValidNil

`func (o *EvidencePackage) SetMerkleProofValidNil(b bool)`

 SetMerkleProofValidNil sets the value for MerkleProofValid to be an explicit nil

### UnsetMerkleProofValid
`func (o *EvidencePackage) UnsetMerkleProofValid()`

UnsetMerkleProofValid ensures that no value is present for MerkleProofValid, not even an explicit nil
### GetSignatureVerification

`func (o *EvidencePackage) GetSignatureVerification() SignatureVerification`

GetSignatureVerification returns the SignatureVerification field if non-nil, zero value otherwise.

### GetSignatureVerificationOk

`func (o *EvidencePackage) GetSignatureVerificationOk() (*SignatureVerification, bool)`

GetSignatureVerificationOk returns a tuple with the SignatureVerification field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignatureVerification

`func (o *EvidencePackage) SetSignatureVerification(v SignatureVerification)`

SetSignatureVerification sets SignatureVerification field to given value.

### HasSignatureVerification

`func (o *EvidencePackage) HasSignatureVerification() bool`

HasSignatureVerification returns a boolean if a field has been set.

### SetSignatureVerificationNil

`func (o *EvidencePackage) SetSignatureVerificationNil(b bool)`

 SetSignatureVerificationNil sets the value for SignatureVerification to be an explicit nil

### UnsetSignatureVerification
`func (o *EvidencePackage) UnsetSignatureVerification()`

UnsetSignatureVerification ensures that no value is present for SignatureVerification, not even an explicit nil
### GetContentMatches

`func (o *EvidencePackage) GetContentMatches() []ContentMatch`

GetContentMatches returns the ContentMatches field if non-nil, zero value otherwise.

### GetContentMatchesOk

`func (o *EvidencePackage) GetContentMatchesOk() (*[]ContentMatch, bool)`

GetContentMatchesOk returns a tuple with the ContentMatches field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentMatches

`func (o *EvidencePackage) SetContentMatches(v []ContentMatch)`

SetContentMatches sets ContentMatches field to given value.

### HasContentMatches

`func (o *EvidencePackage) HasContentMatches() bool`

HasContentMatches returns a boolean if a field has been set.

### GetOriginalTimestamp

`func (o *EvidencePackage) GetOriginalTimestamp() time.Time`

GetOriginalTimestamp returns the OriginalTimestamp field if non-nil, zero value otherwise.

### GetOriginalTimestampOk

`func (o *EvidencePackage) GetOriginalTimestampOk() (*time.Time, bool)`

GetOriginalTimestampOk returns a tuple with the OriginalTimestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOriginalTimestamp

`func (o *EvidencePackage) SetOriginalTimestamp(v time.Time)`

SetOriginalTimestamp sets OriginalTimestamp field to given value.

### HasOriginalTimestamp

`func (o *EvidencePackage) HasOriginalTimestamp() bool`

HasOriginalTimestamp returns a boolean if a field has been set.

### SetOriginalTimestampNil

`func (o *EvidencePackage) SetOriginalTimestampNil(b bool)`

 SetOriginalTimestampNil sets the value for OriginalTimestamp to be an explicit nil

### UnsetOriginalTimestamp
`func (o *EvidencePackage) UnsetOriginalTimestamp()`

UnsetOriginalTimestamp ensures that no value is present for OriginalTimestamp, not even an explicit nil
### GetTimestampVerified

`func (o *EvidencePackage) GetTimestampVerified() bool`

GetTimestampVerified returns the TimestampVerified field if non-nil, zero value otherwise.

### GetTimestampVerifiedOk

`func (o *EvidencePackage) GetTimestampVerifiedOk() (*bool, bool)`

GetTimestampVerifiedOk returns a tuple with the TimestampVerified field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestampVerified

`func (o *EvidencePackage) SetTimestampVerified(v bool)`

SetTimestampVerified sets TimestampVerified field to given value.

### HasTimestampVerified

`func (o *EvidencePackage) HasTimestampVerified() bool`

HasTimestampVerified returns a boolean if a field has been set.

### SetTimestampVerifiedNil

`func (o *EvidencePackage) SetTimestampVerifiedNil(b bool)`

 SetTimestampVerifiedNil sets the value for TimestampVerified to be an explicit nil

### UnsetTimestampVerified
`func (o *EvidencePackage) UnsetTimestampVerified()`

UnsetTimestampVerified ensures that no value is present for TimestampVerified, not even an explicit nil
### GetJsonExportUrl

`func (o *EvidencePackage) GetJsonExportUrl() string`

GetJsonExportUrl returns the JsonExportUrl field if non-nil, zero value otherwise.

### GetJsonExportUrlOk

`func (o *EvidencePackage) GetJsonExportUrlOk() (*string, bool)`

GetJsonExportUrlOk returns a tuple with the JsonExportUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJsonExportUrl

`func (o *EvidencePackage) SetJsonExportUrl(v string)`

SetJsonExportUrl sets JsonExportUrl field to given value.

### HasJsonExportUrl

`func (o *EvidencePackage) HasJsonExportUrl() bool`

HasJsonExportUrl returns a boolean if a field has been set.

### SetJsonExportUrlNil

`func (o *EvidencePackage) SetJsonExportUrlNil(b bool)`

 SetJsonExportUrlNil sets the value for JsonExportUrl to be an explicit nil

### UnsetJsonExportUrl
`func (o *EvidencePackage) UnsetJsonExportUrl()`

UnsetJsonExportUrl ensures that no value is present for JsonExportUrl, not even an explicit nil
### GetPdfExportUrl

`func (o *EvidencePackage) GetPdfExportUrl() string`

GetPdfExportUrl returns the PdfExportUrl field if non-nil, zero value otherwise.

### GetPdfExportUrlOk

`func (o *EvidencePackage) GetPdfExportUrlOk() (*string, bool)`

GetPdfExportUrlOk returns a tuple with the PdfExportUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPdfExportUrl

`func (o *EvidencePackage) SetPdfExportUrl(v string)`

SetPdfExportUrl sets PdfExportUrl field to given value.

### HasPdfExportUrl

`func (o *EvidencePackage) HasPdfExportUrl() bool`

HasPdfExportUrl returns a boolean if a field has been set.

### SetPdfExportUrlNil

`func (o *EvidencePackage) SetPdfExportUrlNil(b bool)`

 SetPdfExportUrlNil sets the value for PdfExportUrl to be an explicit nil

### UnsetPdfExportUrl
`func (o *EvidencePackage) UnsetPdfExportUrl()`

UnsetPdfExportUrl ensures that no value is present for PdfExportUrl, not even an explicit nil
### GetMetadata

`func (o *EvidencePackage) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *EvidencePackage) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *EvidencePackage) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *EvidencePackage) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *EvidencePackage) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *EvidencePackage) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


