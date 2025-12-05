# SourceAttributionRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TextSegment** | **string** | Text segment to search for | 
**SegmentationLevel** | Pointer to **string** | Segmentation level to search at | [optional] [default to "sentence"]
**Normalize** | Pointer to **bool** | Whether to normalize text before hashing | [optional] [default to true]
**IncludeProof** | Pointer to **bool** | Whether to include Merkle proof in response | [optional] [default to false]

## Methods

### NewSourceAttributionRequest

`func NewSourceAttributionRequest(textSegment string, ) *SourceAttributionRequest`

NewSourceAttributionRequest instantiates a new SourceAttributionRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSourceAttributionRequestWithDefaults

`func NewSourceAttributionRequestWithDefaults() *SourceAttributionRequest`

NewSourceAttributionRequestWithDefaults instantiates a new SourceAttributionRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTextSegment

`func (o *SourceAttributionRequest) GetTextSegment() string`

GetTextSegment returns the TextSegment field if non-nil, zero value otherwise.

### GetTextSegmentOk

`func (o *SourceAttributionRequest) GetTextSegmentOk() (*string, bool)`

GetTextSegmentOk returns a tuple with the TextSegment field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextSegment

`func (o *SourceAttributionRequest) SetTextSegment(v string)`

SetTextSegment sets TextSegment field to given value.


### GetSegmentationLevel

`func (o *SourceAttributionRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *SourceAttributionRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *SourceAttributionRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *SourceAttributionRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetNormalize

`func (o *SourceAttributionRequest) GetNormalize() bool`

GetNormalize returns the Normalize field if non-nil, zero value otherwise.

### GetNormalizeOk

`func (o *SourceAttributionRequest) GetNormalizeOk() (*bool, bool)`

GetNormalizeOk returns a tuple with the Normalize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNormalize

`func (o *SourceAttributionRequest) SetNormalize(v bool)`

SetNormalize sets Normalize field to given value.

### HasNormalize

`func (o *SourceAttributionRequest) HasNormalize() bool`

HasNormalize returns a boolean if a field has been set.

### GetIncludeProof

`func (o *SourceAttributionRequest) GetIncludeProof() bool`

GetIncludeProof returns the IncludeProof field if non-nil, zero value otherwise.

### GetIncludeProofOk

`func (o *SourceAttributionRequest) GetIncludeProofOk() (*bool, bool)`

GetIncludeProofOk returns a tuple with the IncludeProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeProof

`func (o *SourceAttributionRequest) SetIncludeProof(v bool)`

SetIncludeProof sets IncludeProof field to given value.

### HasIncludeProof

`func (o *SourceAttributionRequest) HasIncludeProof() bool`

HasIncludeProof returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


