# SourceDocumentMatch

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** |  | 
**OrganizationId** | **string** |  | 
**SegmentationLevel** | **string** |  | 
**MatchedSegments** | **int32** |  | 
**TotalLeaves** | **int32** |  | 
**MatchPercentage** | **float32** |  | 
**ConfidenceScore** | **float32** |  | 
**DocMetadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewSourceDocumentMatch

`func NewSourceDocumentMatch(documentId string, organizationId string, segmentationLevel string, matchedSegments int32, totalLeaves int32, matchPercentage float32, confidenceScore float32, ) *SourceDocumentMatch`

NewSourceDocumentMatch instantiates a new SourceDocumentMatch object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSourceDocumentMatchWithDefaults

`func NewSourceDocumentMatchWithDefaults() *SourceDocumentMatch`

NewSourceDocumentMatchWithDefaults instantiates a new SourceDocumentMatch object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *SourceDocumentMatch) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *SourceDocumentMatch) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *SourceDocumentMatch) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *SourceDocumentMatch) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *SourceDocumentMatch) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *SourceDocumentMatch) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetSegmentationLevel

`func (o *SourceDocumentMatch) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *SourceDocumentMatch) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *SourceDocumentMatch) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.


### GetMatchedSegments

`func (o *SourceDocumentMatch) GetMatchedSegments() int32`

GetMatchedSegments returns the MatchedSegments field if non-nil, zero value otherwise.

### GetMatchedSegmentsOk

`func (o *SourceDocumentMatch) GetMatchedSegmentsOk() (*int32, bool)`

GetMatchedSegmentsOk returns a tuple with the MatchedSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchedSegments

`func (o *SourceDocumentMatch) SetMatchedSegments(v int32)`

SetMatchedSegments sets MatchedSegments field to given value.


### GetTotalLeaves

`func (o *SourceDocumentMatch) GetTotalLeaves() int32`

GetTotalLeaves returns the TotalLeaves field if non-nil, zero value otherwise.

### GetTotalLeavesOk

`func (o *SourceDocumentMatch) GetTotalLeavesOk() (*int32, bool)`

GetTotalLeavesOk returns a tuple with the TotalLeaves field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalLeaves

`func (o *SourceDocumentMatch) SetTotalLeaves(v int32)`

SetTotalLeaves sets TotalLeaves field to given value.


### GetMatchPercentage

`func (o *SourceDocumentMatch) GetMatchPercentage() float32`

GetMatchPercentage returns the MatchPercentage field if non-nil, zero value otherwise.

### GetMatchPercentageOk

`func (o *SourceDocumentMatch) GetMatchPercentageOk() (*float32, bool)`

GetMatchPercentageOk returns a tuple with the MatchPercentage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchPercentage

`func (o *SourceDocumentMatch) SetMatchPercentage(v float32)`

SetMatchPercentage sets MatchPercentage field to given value.


### GetConfidenceScore

`func (o *SourceDocumentMatch) GetConfidenceScore() float32`

GetConfidenceScore returns the ConfidenceScore field if non-nil, zero value otherwise.

### GetConfidenceScoreOk

`func (o *SourceDocumentMatch) GetConfidenceScoreOk() (*float32, bool)`

GetConfidenceScoreOk returns a tuple with the ConfidenceScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidenceScore

`func (o *SourceDocumentMatch) SetConfidenceScore(v float32)`

SetConfidenceScore sets ConfidenceScore field to given value.


### GetDocMetadata

`func (o *SourceDocumentMatch) GetDocMetadata() map[string]interface{}`

GetDocMetadata returns the DocMetadata field if non-nil, zero value otherwise.

### GetDocMetadataOk

`func (o *SourceDocumentMatch) GetDocMetadataOk() (*map[string]interface{}, bool)`

GetDocMetadataOk returns a tuple with the DocMetadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocMetadata

`func (o *SourceDocumentMatch) SetDocMetadata(v map[string]interface{})`

SetDocMetadata sets DocMetadata field to given value.

### HasDocMetadata

`func (o *SourceDocumentMatch) HasDocMetadata() bool`

HasDocMetadata returns a boolean if a field has been set.

### SetDocMetadataNil

`func (o *SourceDocumentMatch) SetDocMetadataNil(b bool)`

 SetDocMetadataNil sets the value for DocMetadata to be an explicit nil

### UnsetDocMetadata
`func (o *SourceDocumentMatch) UnsetDocMetadata()`

UnsetDocMetadata ensures that no value is present for DocMetadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


