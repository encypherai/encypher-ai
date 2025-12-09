# RevocationResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** |  | 
**DocumentId** | **string** |  | 
**Action** | **string** |  | 
**Timestamp** | **string** |  | 
**Message** | **string** |  | 

## Methods

### NewRevocationResponse

`func NewRevocationResponse(success bool, documentId string, action string, timestamp string, message string, ) *RevocationResponse`

NewRevocationResponse instantiates a new RevocationResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRevocationResponseWithDefaults

`func NewRevocationResponseWithDefaults() *RevocationResponse`

NewRevocationResponseWithDefaults instantiates a new RevocationResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *RevocationResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *RevocationResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *RevocationResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetDocumentId

`func (o *RevocationResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *RevocationResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *RevocationResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetAction

`func (o *RevocationResponse) GetAction() string`

GetAction returns the Action field if non-nil, zero value otherwise.

### GetActionOk

`func (o *RevocationResponse) GetActionOk() (*string, bool)`

GetActionOk returns a tuple with the Action field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAction

`func (o *RevocationResponse) SetAction(v string)`

SetAction sets Action field to given value.


### GetTimestamp

`func (o *RevocationResponse) GetTimestamp() string`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *RevocationResponse) GetTimestampOk() (*string, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *RevocationResponse) SetTimestamp(v string)`

SetTimestamp sets Timestamp field to given value.


### GetMessage

`func (o *RevocationResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *RevocationResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *RevocationResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


