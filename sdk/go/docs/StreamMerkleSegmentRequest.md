# StreamMerkleSegmentRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SessionId** | **string** | Session ID from StreamMerkleStartResponse | 
**SegmentText** | **string** | Text segment to add to the tree | 
**SegmentIndex** | Pointer to **NullableInt32** |  | [optional] 
**IsFinal** | Pointer to **bool** | If true, this is the last segment and session should finalize | [optional] [default to false]
**FlushBuffer** | Pointer to **bool** | If true, flush the current buffer to compute intermediate hashes | [optional] [default to false]

## Methods

### NewStreamMerkleSegmentRequest

`func NewStreamMerkleSegmentRequest(sessionId string, segmentText string, ) *StreamMerkleSegmentRequest`

NewStreamMerkleSegmentRequest instantiates a new StreamMerkleSegmentRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleSegmentRequestWithDefaults

`func NewStreamMerkleSegmentRequestWithDefaults() *StreamMerkleSegmentRequest`

NewStreamMerkleSegmentRequestWithDefaults instantiates a new StreamMerkleSegmentRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSessionId

`func (o *StreamMerkleSegmentRequest) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleSegmentRequest) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleSegmentRequest) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetSegmentText

`func (o *StreamMerkleSegmentRequest) GetSegmentText() string`

GetSegmentText returns the SegmentText field if non-nil, zero value otherwise.

### GetSegmentTextOk

`func (o *StreamMerkleSegmentRequest) GetSegmentTextOk() (*string, bool)`

GetSegmentTextOk returns a tuple with the SegmentText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentText

`func (o *StreamMerkleSegmentRequest) SetSegmentText(v string)`

SetSegmentText sets SegmentText field to given value.


### GetSegmentIndex

`func (o *StreamMerkleSegmentRequest) GetSegmentIndex() int32`

GetSegmentIndex returns the SegmentIndex field if non-nil, zero value otherwise.

### GetSegmentIndexOk

`func (o *StreamMerkleSegmentRequest) GetSegmentIndexOk() (*int32, bool)`

GetSegmentIndexOk returns a tuple with the SegmentIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentIndex

`func (o *StreamMerkleSegmentRequest) SetSegmentIndex(v int32)`

SetSegmentIndex sets SegmentIndex field to given value.

### HasSegmentIndex

`func (o *StreamMerkleSegmentRequest) HasSegmentIndex() bool`

HasSegmentIndex returns a boolean if a field has been set.

### SetSegmentIndexNil

`func (o *StreamMerkleSegmentRequest) SetSegmentIndexNil(b bool)`

 SetSegmentIndexNil sets the value for SegmentIndex to be an explicit nil

### UnsetSegmentIndex
`func (o *StreamMerkleSegmentRequest) UnsetSegmentIndex()`

UnsetSegmentIndex ensures that no value is present for SegmentIndex, not even an explicit nil
### GetIsFinal

`func (o *StreamMerkleSegmentRequest) GetIsFinal() bool`

GetIsFinal returns the IsFinal field if non-nil, zero value otherwise.

### GetIsFinalOk

`func (o *StreamMerkleSegmentRequest) GetIsFinalOk() (*bool, bool)`

GetIsFinalOk returns a tuple with the IsFinal field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsFinal

`func (o *StreamMerkleSegmentRequest) SetIsFinal(v bool)`

SetIsFinal sets IsFinal field to given value.

### HasIsFinal

`func (o *StreamMerkleSegmentRequest) HasIsFinal() bool`

HasIsFinal returns a boolean if a field has been set.

### GetFlushBuffer

`func (o *StreamMerkleSegmentRequest) GetFlushBuffer() bool`

GetFlushBuffer returns the FlushBuffer field if non-nil, zero value otherwise.

### GetFlushBufferOk

`func (o *StreamMerkleSegmentRequest) GetFlushBufferOk() (*bool, bool)`

GetFlushBufferOk returns a tuple with the FlushBuffer field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFlushBuffer

`func (o *StreamMerkleSegmentRequest) SetFlushBuffer(v bool)`

SetFlushBuffer sets FlushBuffer field to given value.

### HasFlushBuffer

`func (o *StreamMerkleSegmentRequest) HasFlushBuffer() bool`

HasFlushBuffer returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


