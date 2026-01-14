# StreamMerkleStartResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether session was created successfully | 
**SessionId** | **string** | Unique session identifier for subsequent calls | 
**DocumentId** | **string** | Document identifier | 
**ExpiresAt** | **time.Time** | When the session will expire if idle | 
**BufferSize** | **int32** | Maximum buffer size before auto-flush | 
**Message** | **string** | Status message | 

## Methods

### NewStreamMerkleStartResponse

`func NewStreamMerkleStartResponse(success bool, sessionId string, documentId string, expiresAt time.Time, bufferSize int32, message string, ) *StreamMerkleStartResponse`

NewStreamMerkleStartResponse instantiates a new StreamMerkleStartResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleStartResponseWithDefaults

`func NewStreamMerkleStartResponseWithDefaults() *StreamMerkleStartResponse`

NewStreamMerkleStartResponseWithDefaults instantiates a new StreamMerkleStartResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *StreamMerkleStartResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *StreamMerkleStartResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *StreamMerkleStartResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetSessionId

`func (o *StreamMerkleStartResponse) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleStartResponse) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleStartResponse) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetDocumentId

`func (o *StreamMerkleStartResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *StreamMerkleStartResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *StreamMerkleStartResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetExpiresAt

`func (o *StreamMerkleStartResponse) GetExpiresAt() time.Time`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *StreamMerkleStartResponse) GetExpiresAtOk() (*time.Time, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *StreamMerkleStartResponse) SetExpiresAt(v time.Time)`

SetExpiresAt sets ExpiresAt field to given value.


### GetBufferSize

`func (o *StreamMerkleStartResponse) GetBufferSize() int32`

GetBufferSize returns the BufferSize field if non-nil, zero value otherwise.

### GetBufferSizeOk

`func (o *StreamMerkleStartResponse) GetBufferSizeOk() (*int32, bool)`

GetBufferSizeOk returns a tuple with the BufferSize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBufferSize

`func (o *StreamMerkleStartResponse) SetBufferSize(v int32)`

SetBufferSize sets BufferSize field to given value.


### GetMessage

`func (o *StreamMerkleStartResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *StreamMerkleStartResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *StreamMerkleStartResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


