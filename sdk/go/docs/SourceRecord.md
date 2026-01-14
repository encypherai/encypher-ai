# SourceRecord

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Source document ID | 
**OrganizationId** | **string** | Source organization ID | 
**OrganizationName** | Pointer to **NullableString** |  | [optional] 
**SegmentHash** | **string** | Hash of the matched segment | 
**LeafIndex** | **int32** | Index in source Merkle tree | 
**MerkleRootHash** | Pointer to **NullableString** |  | [optional] 
**CreatedAt** | **time.Time** | When content was first registered | 
**SignedAt** | Pointer to **NullableTime** |  | [optional] 
**Confidence** | **float32** | Match confidence (0-1) | 
**AuthorityScore** | Pointer to **NullableFloat32** |  | [optional] 
**IsOriginal** | **bool** | Whether this is the original source | 
**PreviousSourceId** | Pointer to **NullableString** |  | [optional] 
**NextSourceId** | Pointer to **NullableString** |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewSourceRecord

`func NewSourceRecord(documentId string, organizationId string, segmentHash string, leafIndex int32, createdAt time.Time, confidence float32, isOriginal bool, ) *SourceRecord`

NewSourceRecord instantiates a new SourceRecord object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSourceRecordWithDefaults

`func NewSourceRecordWithDefaults() *SourceRecord`

NewSourceRecordWithDefaults instantiates a new SourceRecord object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *SourceRecord) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *SourceRecord) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *SourceRecord) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *SourceRecord) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *SourceRecord) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *SourceRecord) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetOrganizationName

`func (o *SourceRecord) GetOrganizationName() string`

GetOrganizationName returns the OrganizationName field if non-nil, zero value otherwise.

### GetOrganizationNameOk

`func (o *SourceRecord) GetOrganizationNameOk() (*string, bool)`

GetOrganizationNameOk returns a tuple with the OrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationName

`func (o *SourceRecord) SetOrganizationName(v string)`

SetOrganizationName sets OrganizationName field to given value.

### HasOrganizationName

`func (o *SourceRecord) HasOrganizationName() bool`

HasOrganizationName returns a boolean if a field has been set.

### SetOrganizationNameNil

`func (o *SourceRecord) SetOrganizationNameNil(b bool)`

 SetOrganizationNameNil sets the value for OrganizationName to be an explicit nil

### UnsetOrganizationName
`func (o *SourceRecord) UnsetOrganizationName()`

UnsetOrganizationName ensures that no value is present for OrganizationName, not even an explicit nil
### GetSegmentHash

`func (o *SourceRecord) GetSegmentHash() string`

GetSegmentHash returns the SegmentHash field if non-nil, zero value otherwise.

### GetSegmentHashOk

`func (o *SourceRecord) GetSegmentHashOk() (*string, bool)`

GetSegmentHashOk returns a tuple with the SegmentHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentHash

`func (o *SourceRecord) SetSegmentHash(v string)`

SetSegmentHash sets SegmentHash field to given value.


### GetLeafIndex

`func (o *SourceRecord) GetLeafIndex() int32`

GetLeafIndex returns the LeafIndex field if non-nil, zero value otherwise.

### GetLeafIndexOk

`func (o *SourceRecord) GetLeafIndexOk() (*int32, bool)`

GetLeafIndexOk returns a tuple with the LeafIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafIndex

`func (o *SourceRecord) SetLeafIndex(v int32)`

SetLeafIndex sets LeafIndex field to given value.


### GetMerkleRootHash

`func (o *SourceRecord) GetMerkleRootHash() string`

GetMerkleRootHash returns the MerkleRootHash field if non-nil, zero value otherwise.

### GetMerkleRootHashOk

`func (o *SourceRecord) GetMerkleRootHashOk() (*string, bool)`

GetMerkleRootHashOk returns a tuple with the MerkleRootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleRootHash

`func (o *SourceRecord) SetMerkleRootHash(v string)`

SetMerkleRootHash sets MerkleRootHash field to given value.

### HasMerkleRootHash

`func (o *SourceRecord) HasMerkleRootHash() bool`

HasMerkleRootHash returns a boolean if a field has been set.

### SetMerkleRootHashNil

`func (o *SourceRecord) SetMerkleRootHashNil(b bool)`

 SetMerkleRootHashNil sets the value for MerkleRootHash to be an explicit nil

### UnsetMerkleRootHash
`func (o *SourceRecord) UnsetMerkleRootHash()`

UnsetMerkleRootHash ensures that no value is present for MerkleRootHash, not even an explicit nil
### GetCreatedAt

`func (o *SourceRecord) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *SourceRecord) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *SourceRecord) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetSignedAt

`func (o *SourceRecord) GetSignedAt() time.Time`

GetSignedAt returns the SignedAt field if non-nil, zero value otherwise.

### GetSignedAtOk

`func (o *SourceRecord) GetSignedAtOk() (*time.Time, bool)`

GetSignedAtOk returns a tuple with the SignedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedAt

`func (o *SourceRecord) SetSignedAt(v time.Time)`

SetSignedAt sets SignedAt field to given value.

### HasSignedAt

`func (o *SourceRecord) HasSignedAt() bool`

HasSignedAt returns a boolean if a field has been set.

### SetSignedAtNil

`func (o *SourceRecord) SetSignedAtNil(b bool)`

 SetSignedAtNil sets the value for SignedAt to be an explicit nil

### UnsetSignedAt
`func (o *SourceRecord) UnsetSignedAt()`

UnsetSignedAt ensures that no value is present for SignedAt, not even an explicit nil
### GetConfidence

`func (o *SourceRecord) GetConfidence() float32`

GetConfidence returns the Confidence field if non-nil, zero value otherwise.

### GetConfidenceOk

`func (o *SourceRecord) GetConfidenceOk() (*float32, bool)`

GetConfidenceOk returns a tuple with the Confidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidence

`func (o *SourceRecord) SetConfidence(v float32)`

SetConfidence sets Confidence field to given value.


### GetAuthorityScore

`func (o *SourceRecord) GetAuthorityScore() float32`

GetAuthorityScore returns the AuthorityScore field if non-nil, zero value otherwise.

### GetAuthorityScoreOk

`func (o *SourceRecord) GetAuthorityScoreOk() (*float32, bool)`

GetAuthorityScoreOk returns a tuple with the AuthorityScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuthorityScore

`func (o *SourceRecord) SetAuthorityScore(v float32)`

SetAuthorityScore sets AuthorityScore field to given value.

### HasAuthorityScore

`func (o *SourceRecord) HasAuthorityScore() bool`

HasAuthorityScore returns a boolean if a field has been set.

### SetAuthorityScoreNil

`func (o *SourceRecord) SetAuthorityScoreNil(b bool)`

 SetAuthorityScoreNil sets the value for AuthorityScore to be an explicit nil

### UnsetAuthorityScore
`func (o *SourceRecord) UnsetAuthorityScore()`

UnsetAuthorityScore ensures that no value is present for AuthorityScore, not even an explicit nil
### GetIsOriginal

`func (o *SourceRecord) GetIsOriginal() bool`

GetIsOriginal returns the IsOriginal field if non-nil, zero value otherwise.

### GetIsOriginalOk

`func (o *SourceRecord) GetIsOriginalOk() (*bool, bool)`

GetIsOriginalOk returns a tuple with the IsOriginal field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsOriginal

`func (o *SourceRecord) SetIsOriginal(v bool)`

SetIsOriginal sets IsOriginal field to given value.


### GetPreviousSourceId

`func (o *SourceRecord) GetPreviousSourceId() string`

GetPreviousSourceId returns the PreviousSourceId field if non-nil, zero value otherwise.

### GetPreviousSourceIdOk

`func (o *SourceRecord) GetPreviousSourceIdOk() (*string, bool)`

GetPreviousSourceIdOk returns a tuple with the PreviousSourceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPreviousSourceId

`func (o *SourceRecord) SetPreviousSourceId(v string)`

SetPreviousSourceId sets PreviousSourceId field to given value.

### HasPreviousSourceId

`func (o *SourceRecord) HasPreviousSourceId() bool`

HasPreviousSourceId returns a boolean if a field has been set.

### SetPreviousSourceIdNil

`func (o *SourceRecord) SetPreviousSourceIdNil(b bool)`

 SetPreviousSourceIdNil sets the value for PreviousSourceId to be an explicit nil

### UnsetPreviousSourceId
`func (o *SourceRecord) UnsetPreviousSourceId()`

UnsetPreviousSourceId ensures that no value is present for PreviousSourceId, not even an explicit nil
### GetNextSourceId

`func (o *SourceRecord) GetNextSourceId() string`

GetNextSourceId returns the NextSourceId field if non-nil, zero value otherwise.

### GetNextSourceIdOk

`func (o *SourceRecord) GetNextSourceIdOk() (*string, bool)`

GetNextSourceIdOk returns a tuple with the NextSourceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNextSourceId

`func (o *SourceRecord) SetNextSourceId(v string)`

SetNextSourceId sets NextSourceId field to given value.

### HasNextSourceId

`func (o *SourceRecord) HasNextSourceId() bool`

HasNextSourceId returns a boolean if a field has been set.

### SetNextSourceIdNil

`func (o *SourceRecord) SetNextSourceIdNil(b bool)`

 SetNextSourceIdNil sets the value for NextSourceId to be an explicit nil

### UnsetNextSourceId
`func (o *SourceRecord) UnsetNextSourceId()`

UnsetNextSourceId ensures that no value is present for NextSourceId, not even an explicit nil
### GetMetadata

`func (o *SourceRecord) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *SourceRecord) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *SourceRecord) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *SourceRecord) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *SourceRecord) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *SourceRecord) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


