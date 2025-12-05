# SuccessResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Message** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewSuccessResponse

`func NewSuccessResponse() *SuccessResponse`

NewSuccessResponse instantiates a new SuccessResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSuccessResponseWithDefaults

`func NewSuccessResponseWithDefaults() *SuccessResponse`

NewSuccessResponseWithDefaults instantiates a new SuccessResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *SuccessResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *SuccessResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *SuccessResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *SuccessResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetMessage

`func (o *SuccessResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *SuccessResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *SuccessResponse) SetMessage(v string)`

SetMessage sets Message field to given value.

### HasMessage

`func (o *SuccessResponse) HasMessage() bool`

HasMessage returns a boolean if a field has been set.

### SetMessageNil

`func (o *SuccessResponse) SetMessageNil(b bool)`

 SetMessageNil sets the value for Message to be an explicit nil

### UnsetMessage
`func (o *SuccessResponse) UnsetMessage()`

UnsetMessage ensures that no value is present for Message, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


