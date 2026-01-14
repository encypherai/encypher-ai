# StreamMerkleFinalizeResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether finalization was successful | 
**SessionId** | **string** | Session identifier | 
**DocumentId** | **string** | Document identifier | 
**RootHash** | **string** | Final Merkle root hash | 
**TreeDepth** | **int32** | Depth of the Merkle tree | 
**TotalSegments** | **int32** | Total number of segments in tree | 
**EmbeddedContent** | Pointer to **NullableString** |  | [optional] 
**InstanceId** | Pointer to **NullableString** |  | [optional] 
**ProcessingTimeMs** | **float32** | Total processing time in milliseconds | 
**Message** | **string** | Status message | 

## Methods

### NewStreamMerkleFinalizeResponse

`func NewStreamMerkleFinalizeResponse(success bool, sessionId string, documentId string, rootHash string, treeDepth int32, totalSegments int32, processingTimeMs float32, message string, ) *StreamMerkleFinalizeResponse`

NewStreamMerkleFinalizeResponse instantiates a new StreamMerkleFinalizeResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleFinalizeResponseWithDefaults

`func NewStreamMerkleFinalizeResponseWithDefaults() *StreamMerkleFinalizeResponse`

NewStreamMerkleFinalizeResponseWithDefaults instantiates a new StreamMerkleFinalizeResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *StreamMerkleFinalizeResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *StreamMerkleFinalizeResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *StreamMerkleFinalizeResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetSessionId

`func (o *StreamMerkleFinalizeResponse) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleFinalizeResponse) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleFinalizeResponse) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetDocumentId

`func (o *StreamMerkleFinalizeResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *StreamMerkleFinalizeResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *StreamMerkleFinalizeResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetRootHash

`func (o *StreamMerkleFinalizeResponse) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *StreamMerkleFinalizeResponse) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *StreamMerkleFinalizeResponse) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetTreeDepth

`func (o *StreamMerkleFinalizeResponse) GetTreeDepth() int32`

GetTreeDepth returns the TreeDepth field if non-nil, zero value otherwise.

### GetTreeDepthOk

`func (o *StreamMerkleFinalizeResponse) GetTreeDepthOk() (*int32, bool)`

GetTreeDepthOk returns a tuple with the TreeDepth field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTreeDepth

`func (o *StreamMerkleFinalizeResponse) SetTreeDepth(v int32)`

SetTreeDepth sets TreeDepth field to given value.


### GetTotalSegments

`func (o *StreamMerkleFinalizeResponse) GetTotalSegments() int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *StreamMerkleFinalizeResponse) GetTotalSegmentsOk() (*int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *StreamMerkleFinalizeResponse) SetTotalSegments(v int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetEmbeddedContent

`func (o *StreamMerkleFinalizeResponse) GetEmbeddedContent() string`

GetEmbeddedContent returns the EmbeddedContent field if non-nil, zero value otherwise.

### GetEmbeddedContentOk

`func (o *StreamMerkleFinalizeResponse) GetEmbeddedContentOk() (*string, bool)`

GetEmbeddedContentOk returns a tuple with the EmbeddedContent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddedContent

`func (o *StreamMerkleFinalizeResponse) SetEmbeddedContent(v string)`

SetEmbeddedContent sets EmbeddedContent field to given value.

### HasEmbeddedContent

`func (o *StreamMerkleFinalizeResponse) HasEmbeddedContent() bool`

HasEmbeddedContent returns a boolean if a field has been set.

### SetEmbeddedContentNil

`func (o *StreamMerkleFinalizeResponse) SetEmbeddedContentNil(b bool)`

 SetEmbeddedContentNil sets the value for EmbeddedContent to be an explicit nil

### UnsetEmbeddedContent
`func (o *StreamMerkleFinalizeResponse) UnsetEmbeddedContent()`

UnsetEmbeddedContent ensures that no value is present for EmbeddedContent, not even an explicit nil
### GetInstanceId

`func (o *StreamMerkleFinalizeResponse) GetInstanceId() string`

GetInstanceId returns the InstanceId field if non-nil, zero value otherwise.

### GetInstanceIdOk

`func (o *StreamMerkleFinalizeResponse) GetInstanceIdOk() (*string, bool)`

GetInstanceIdOk returns a tuple with the InstanceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInstanceId

`func (o *StreamMerkleFinalizeResponse) SetInstanceId(v string)`

SetInstanceId sets InstanceId field to given value.

### HasInstanceId

`func (o *StreamMerkleFinalizeResponse) HasInstanceId() bool`

HasInstanceId returns a boolean if a field has been set.

### SetInstanceIdNil

`func (o *StreamMerkleFinalizeResponse) SetInstanceIdNil(b bool)`

 SetInstanceIdNil sets the value for InstanceId to be an explicit nil

### UnsetInstanceId
`func (o *StreamMerkleFinalizeResponse) UnsetInstanceId()`

UnsetInstanceId ensures that no value is present for InstanceId, not even an explicit nil
### GetProcessingTimeMs

`func (o *StreamMerkleFinalizeResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *StreamMerkleFinalizeResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *StreamMerkleFinalizeResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetMessage

`func (o *StreamMerkleFinalizeResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *StreamMerkleFinalizeResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *StreamMerkleFinalizeResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


