# StreamMerkleStatusResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether status check was successful | 
**SessionId** | **string** | Session identifier | 
**DocumentId** | **string** | Document identifier | 
**Status** | **string** | Session status: active, finalized, expired | 
**TotalSegments** | **int32** | Total segments added | 
**BufferCount** | **int32** | Segments currently in buffer | 
**IntermediateRoot** | Pointer to **NullableString** |  | [optional] 
**CreatedAt** | **time.Time** | When session was created | 
**ExpiresAt** | **time.Time** | When session will expire | 
**LastActivity** | **time.Time** | Last activity timestamp | 

## Methods

### NewStreamMerkleStatusResponse

`func NewStreamMerkleStatusResponse(success bool, sessionId string, documentId string, status string, totalSegments int32, bufferCount int32, createdAt time.Time, expiresAt time.Time, lastActivity time.Time, ) *StreamMerkleStatusResponse`

NewStreamMerkleStatusResponse instantiates a new StreamMerkleStatusResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleStatusResponseWithDefaults

`func NewStreamMerkleStatusResponseWithDefaults() *StreamMerkleStatusResponse`

NewStreamMerkleStatusResponseWithDefaults instantiates a new StreamMerkleStatusResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *StreamMerkleStatusResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *StreamMerkleStatusResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *StreamMerkleStatusResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetSessionId

`func (o *StreamMerkleStatusResponse) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleStatusResponse) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleStatusResponse) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetDocumentId

`func (o *StreamMerkleStatusResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *StreamMerkleStatusResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *StreamMerkleStatusResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetStatus

`func (o *StreamMerkleStatusResponse) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *StreamMerkleStatusResponse) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *StreamMerkleStatusResponse) SetStatus(v string)`

SetStatus sets Status field to given value.


### GetTotalSegments

`func (o *StreamMerkleStatusResponse) GetTotalSegments() int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *StreamMerkleStatusResponse) GetTotalSegmentsOk() (*int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *StreamMerkleStatusResponse) SetTotalSegments(v int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetBufferCount

`func (o *StreamMerkleStatusResponse) GetBufferCount() int32`

GetBufferCount returns the BufferCount field if non-nil, zero value otherwise.

### GetBufferCountOk

`func (o *StreamMerkleStatusResponse) GetBufferCountOk() (*int32, bool)`

GetBufferCountOk returns a tuple with the BufferCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBufferCount

`func (o *StreamMerkleStatusResponse) SetBufferCount(v int32)`

SetBufferCount sets BufferCount field to given value.


### GetIntermediateRoot

`func (o *StreamMerkleStatusResponse) GetIntermediateRoot() string`

GetIntermediateRoot returns the IntermediateRoot field if non-nil, zero value otherwise.

### GetIntermediateRootOk

`func (o *StreamMerkleStatusResponse) GetIntermediateRootOk() (*string, bool)`

GetIntermediateRootOk returns a tuple with the IntermediateRoot field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIntermediateRoot

`func (o *StreamMerkleStatusResponse) SetIntermediateRoot(v string)`

SetIntermediateRoot sets IntermediateRoot field to given value.

### HasIntermediateRoot

`func (o *StreamMerkleStatusResponse) HasIntermediateRoot() bool`

HasIntermediateRoot returns a boolean if a field has been set.

### SetIntermediateRootNil

`func (o *StreamMerkleStatusResponse) SetIntermediateRootNil(b bool)`

 SetIntermediateRootNil sets the value for IntermediateRoot to be an explicit nil

### UnsetIntermediateRoot
`func (o *StreamMerkleStatusResponse) UnsetIntermediateRoot()`

UnsetIntermediateRoot ensures that no value is present for IntermediateRoot, not even an explicit nil
### GetCreatedAt

`func (o *StreamMerkleStatusResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *StreamMerkleStatusResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *StreamMerkleStatusResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetExpiresAt

`func (o *StreamMerkleStatusResponse) GetExpiresAt() time.Time`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *StreamMerkleStatusResponse) GetExpiresAtOk() (*time.Time, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *StreamMerkleStatusResponse) SetExpiresAt(v time.Time)`

SetExpiresAt sets ExpiresAt field to given value.


### GetLastActivity

`func (o *StreamMerkleStatusResponse) GetLastActivity() time.Time`

GetLastActivity returns the LastActivity field if non-nil, zero value otherwise.

### GetLastActivityOk

`func (o *StreamMerkleStatusResponse) GetLastActivityOk() (*time.Time, bool)`

GetLastActivityOk returns a tuple with the LastActivity field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastActivity

`func (o *StreamMerkleStatusResponse) SetLastActivity(v time.Time)`

SetLastActivity sets LastActivity field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


