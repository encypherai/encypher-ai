# SourceMatch

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Source document identifier | 
**OrganizationId** | **string** | Organization that owns the document | 
**RootHash** | **string** | Merkle root hash | 
**SegmentationLevel** | **string** | Segmentation level | 
**MatchedHash** | **string** | Hash that matched | 
**TextContent** | Pointer to **NullableString** |  | [optional] 
**Confidence** | **float32** | Confidence score (0-1) | 

## Methods

### NewSourceMatch

`func NewSourceMatch(documentId string, organizationId string, rootHash string, segmentationLevel string, matchedHash string, confidence float32, ) *SourceMatch`

NewSourceMatch instantiates a new SourceMatch object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSourceMatchWithDefaults

`func NewSourceMatchWithDefaults() *SourceMatch`

NewSourceMatchWithDefaults instantiates a new SourceMatch object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *SourceMatch) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *SourceMatch) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *SourceMatch) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *SourceMatch) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *SourceMatch) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *SourceMatch) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetRootHash

`func (o *SourceMatch) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *SourceMatch) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *SourceMatch) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetSegmentationLevel

`func (o *SourceMatch) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *SourceMatch) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *SourceMatch) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.


### GetMatchedHash

`func (o *SourceMatch) GetMatchedHash() string`

GetMatchedHash returns the MatchedHash field if non-nil, zero value otherwise.

### GetMatchedHashOk

`func (o *SourceMatch) GetMatchedHashOk() (*string, bool)`

GetMatchedHashOk returns a tuple with the MatchedHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchedHash

`func (o *SourceMatch) SetMatchedHash(v string)`

SetMatchedHash sets MatchedHash field to given value.


### GetTextContent

`func (o *SourceMatch) GetTextContent() string`

GetTextContent returns the TextContent field if non-nil, zero value otherwise.

### GetTextContentOk

`func (o *SourceMatch) GetTextContentOk() (*string, bool)`

GetTextContentOk returns a tuple with the TextContent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextContent

`func (o *SourceMatch) SetTextContent(v string)`

SetTextContent sets TextContent field to given value.

### HasTextContent

`func (o *SourceMatch) HasTextContent() bool`

HasTextContent returns a boolean if a field has been set.

### SetTextContentNil

`func (o *SourceMatch) SetTextContentNil(b bool)`

 SetTextContentNil sets the value for TextContent to be an explicit nil

### UnsetTextContent
`func (o *SourceMatch) UnsetTextContent()`

UnsetTextContent ensures that no value is present for TextContent, not even an explicit nil
### GetConfidence

`func (o *SourceMatch) GetConfidence() float32`

GetConfidence returns the Confidence field if non-nil, zero value otherwise.

### GetConfidenceOk

`func (o *SourceMatch) GetConfidenceOk() (*float32, bool)`

GetConfidenceOk returns a tuple with the Confidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidence

`func (o *SourceMatch) SetConfidence(v float32)`

SetConfidence sets Confidence field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


