# StreamMerkleSegmentResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether segment was added successfully | 
**SessionId** | **string** | Session identifier | 
**SegmentIndex** | **int32** | Index of the added segment | 
**SegmentHash** | **string** | SHA-256 hash of the segment | 
**BufferCount** | **int32** | Current number of segments in buffer | 
**TotalSegments** | **int32** | Total segments added to session | 
**IntermediateRoot** | Pointer to **NullableString** |  | [optional] 
**Message** | **string** | Status message | 

## Methods

### NewStreamMerkleSegmentResponse

`func NewStreamMerkleSegmentResponse(success bool, sessionId string, segmentIndex int32, segmentHash string, bufferCount int32, totalSegments int32, message string, ) *StreamMerkleSegmentResponse`

NewStreamMerkleSegmentResponse instantiates a new StreamMerkleSegmentResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleSegmentResponseWithDefaults

`func NewStreamMerkleSegmentResponseWithDefaults() *StreamMerkleSegmentResponse`

NewStreamMerkleSegmentResponseWithDefaults instantiates a new StreamMerkleSegmentResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *StreamMerkleSegmentResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *StreamMerkleSegmentResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *StreamMerkleSegmentResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetSessionId

`func (o *StreamMerkleSegmentResponse) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleSegmentResponse) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleSegmentResponse) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetSegmentIndex

`func (o *StreamMerkleSegmentResponse) GetSegmentIndex() int32`

GetSegmentIndex returns the SegmentIndex field if non-nil, zero value otherwise.

### GetSegmentIndexOk

`func (o *StreamMerkleSegmentResponse) GetSegmentIndexOk() (*int32, bool)`

GetSegmentIndexOk returns a tuple with the SegmentIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentIndex

`func (o *StreamMerkleSegmentResponse) SetSegmentIndex(v int32)`

SetSegmentIndex sets SegmentIndex field to given value.


### GetSegmentHash

`func (o *StreamMerkleSegmentResponse) GetSegmentHash() string`

GetSegmentHash returns the SegmentHash field if non-nil, zero value otherwise.

### GetSegmentHashOk

`func (o *StreamMerkleSegmentResponse) GetSegmentHashOk() (*string, bool)`

GetSegmentHashOk returns a tuple with the SegmentHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentHash

`func (o *StreamMerkleSegmentResponse) SetSegmentHash(v string)`

SetSegmentHash sets SegmentHash field to given value.


### GetBufferCount

`func (o *StreamMerkleSegmentResponse) GetBufferCount() int32`

GetBufferCount returns the BufferCount field if non-nil, zero value otherwise.

### GetBufferCountOk

`func (o *StreamMerkleSegmentResponse) GetBufferCountOk() (*int32, bool)`

GetBufferCountOk returns a tuple with the BufferCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBufferCount

`func (o *StreamMerkleSegmentResponse) SetBufferCount(v int32)`

SetBufferCount sets BufferCount field to given value.


### GetTotalSegments

`func (o *StreamMerkleSegmentResponse) GetTotalSegments() int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *StreamMerkleSegmentResponse) GetTotalSegmentsOk() (*int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *StreamMerkleSegmentResponse) SetTotalSegments(v int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetIntermediateRoot

`func (o *StreamMerkleSegmentResponse) GetIntermediateRoot() string`

GetIntermediateRoot returns the IntermediateRoot field if non-nil, zero value otherwise.

### GetIntermediateRootOk

`func (o *StreamMerkleSegmentResponse) GetIntermediateRootOk() (*string, bool)`

GetIntermediateRootOk returns a tuple with the IntermediateRoot field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIntermediateRoot

`func (o *StreamMerkleSegmentResponse) SetIntermediateRoot(v string)`

SetIntermediateRoot sets IntermediateRoot field to given value.

### HasIntermediateRoot

`func (o *StreamMerkleSegmentResponse) HasIntermediateRoot() bool`

HasIntermediateRoot returns a boolean if a field has been set.

### SetIntermediateRootNil

`func (o *StreamMerkleSegmentResponse) SetIntermediateRootNil(b bool)`

 SetIntermediateRootNil sets the value for IntermediateRoot to be an explicit nil

### UnsetIntermediateRoot
`func (o *StreamMerkleSegmentResponse) UnsetIntermediateRoot()`

UnsetIntermediateRoot ensures that no value is present for IntermediateRoot, not even an explicit nil
### GetMessage

`func (o *StreamMerkleSegmentResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *StreamMerkleSegmentResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *StreamMerkleSegmentResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


