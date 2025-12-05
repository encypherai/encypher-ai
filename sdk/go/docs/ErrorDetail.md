# ErrorDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Code** | **string** | Stable machine-readable error code | 
**Message** | **string** | Human readable error description | 
**Hint** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewErrorDetail

`func NewErrorDetail(code string, message string, ) *ErrorDetail`

NewErrorDetail instantiates a new ErrorDetail object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewErrorDetailWithDefaults

`func NewErrorDetailWithDefaults() *ErrorDetail`

NewErrorDetailWithDefaults instantiates a new ErrorDetail object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCode

`func (o *ErrorDetail) GetCode() string`

GetCode returns the Code field if non-nil, zero value otherwise.

### GetCodeOk

`func (o *ErrorDetail) GetCodeOk() (*string, bool)`

GetCodeOk returns a tuple with the Code field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCode

`func (o *ErrorDetail) SetCode(v string)`

SetCode sets Code field to given value.


### GetMessage

`func (o *ErrorDetail) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *ErrorDetail) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *ErrorDetail) SetMessage(v string)`

SetMessage sets Message field to given value.


### GetHint

`func (o *ErrorDetail) GetHint() string`

GetHint returns the Hint field if non-nil, zero value otherwise.

### GetHintOk

`func (o *ErrorDetail) GetHintOk() (*string, bool)`

GetHintOk returns a tuple with the Hint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHint

`func (o *ErrorDetail) SetHint(v string)`

SetHint sets Hint field to given value.

### HasHint

`func (o *ErrorDetail) HasHint() bool`

HasHint returns a boolean if a field has been set.

### SetHintNil

`func (o *ErrorDetail) SetHintNil(b bool)`

 SetHintNil sets the value for Hint to be an explicit nil

### UnsetHint
`func (o *ErrorDetail) UnsetHint()`

UnsetHint ensures that no value is present for Hint, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


