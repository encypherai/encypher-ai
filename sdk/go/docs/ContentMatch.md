# ContentMatch

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SegmentText** | **string** | Matched text segment | 
**SegmentHash** | **string** | Hash of the segment | 
**LeafIndex** | **int32** | Index in Merkle tree | 
**Confidence** | **float32** | Match confidence (0-1) | 
**SourceDocumentId** | **string** | Source document ID | 
**SourceOrganizationId** | **string** | Source organization ID | 

## Methods

### NewContentMatch

`func NewContentMatch(segmentText string, segmentHash string, leafIndex int32, confidence float32, sourceDocumentId string, sourceOrganizationId string, ) *ContentMatch`

NewContentMatch instantiates a new ContentMatch object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentMatchWithDefaults

`func NewContentMatchWithDefaults() *ContentMatch`

NewContentMatchWithDefaults instantiates a new ContentMatch object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSegmentText

`func (o *ContentMatch) GetSegmentText() string`

GetSegmentText returns the SegmentText field if non-nil, zero value otherwise.

### GetSegmentTextOk

`func (o *ContentMatch) GetSegmentTextOk() (*string, bool)`

GetSegmentTextOk returns a tuple with the SegmentText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentText

`func (o *ContentMatch) SetSegmentText(v string)`

SetSegmentText sets SegmentText field to given value.


### GetSegmentHash

`func (o *ContentMatch) GetSegmentHash() string`

GetSegmentHash returns the SegmentHash field if non-nil, zero value otherwise.

### GetSegmentHashOk

`func (o *ContentMatch) GetSegmentHashOk() (*string, bool)`

GetSegmentHashOk returns a tuple with the SegmentHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentHash

`func (o *ContentMatch) SetSegmentHash(v string)`

SetSegmentHash sets SegmentHash field to given value.


### GetLeafIndex

`func (o *ContentMatch) GetLeafIndex() int32`

GetLeafIndex returns the LeafIndex field if non-nil, zero value otherwise.

### GetLeafIndexOk

`func (o *ContentMatch) GetLeafIndexOk() (*int32, bool)`

GetLeafIndexOk returns a tuple with the LeafIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafIndex

`func (o *ContentMatch) SetLeafIndex(v int32)`

SetLeafIndex sets LeafIndex field to given value.


### GetConfidence

`func (o *ContentMatch) GetConfidence() float32`

GetConfidence returns the Confidence field if non-nil, zero value otherwise.

### GetConfidenceOk

`func (o *ContentMatch) GetConfidenceOk() (*float32, bool)`

GetConfidenceOk returns a tuple with the Confidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidence

`func (o *ContentMatch) SetConfidence(v float32)`

SetConfidence sets Confidence field to given value.


### GetSourceDocumentId

`func (o *ContentMatch) GetSourceDocumentId() string`

GetSourceDocumentId returns the SourceDocumentId field if non-nil, zero value otherwise.

### GetSourceDocumentIdOk

`func (o *ContentMatch) GetSourceDocumentIdOk() (*string, bool)`

GetSourceDocumentIdOk returns a tuple with the SourceDocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceDocumentId

`func (o *ContentMatch) SetSourceDocumentId(v string)`

SetSourceDocumentId sets SourceDocumentId field to given value.


### GetSourceOrganizationId

`func (o *ContentMatch) GetSourceOrganizationId() string`

GetSourceOrganizationId returns the SourceOrganizationId field if non-nil, zero value otherwise.

### GetSourceOrganizationIdOk

`func (o *ContentMatch) GetSourceOrganizationIdOk() (*string, bool)`

GetSourceOrganizationIdOk returns a tuple with the SourceOrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceOrganizationId

`func (o *ContentMatch) SetSourceOrganizationId(v string)`

SetSourceOrganizationId sets SourceOrganizationId field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


