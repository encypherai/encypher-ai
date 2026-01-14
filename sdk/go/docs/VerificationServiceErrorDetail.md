# VerificationServiceErrorDetail

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Code** | **string** |  | 
**Message** | **string** |  | 
**Hint** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewVerificationServiceErrorDetail

`func NewVerificationServiceErrorDetail(code string, message string, ) *VerificationServiceErrorDetail`

NewVerificationServiceErrorDetail instantiates a new VerificationServiceErrorDetail object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationServiceErrorDetailWithDefaults

`func NewVerificationServiceErrorDetailWithDefaults() *VerificationServiceErrorDetail`

NewVerificationServiceErrorDetailWithDefaults instantiates a new VerificationServiceErrorDetail object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCode

`func (o *VerificationServiceErrorDetail) GetCode() string`

GetCode returns the Code field if non-nil, zero value otherwise.

### GetCodeOk

`func (o *VerificationServiceErrorDetail) GetCodeOk() (*string, bool)`

GetCodeOk returns a tuple with the Code field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCode

`func (o *VerificationServiceErrorDetail) SetCode(v string)`

SetCode sets Code field to given value.


### GetMessage

`func (o *VerificationServiceErrorDetail) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *VerificationServiceErrorDetail) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *VerificationServiceErrorDetail) SetMessage(v string)`

SetMessage sets Message field to given value.


### GetHint

`func (o *VerificationServiceErrorDetail) GetHint() string`

GetHint returns the Hint field if non-nil, zero value otherwise.

### GetHintOk

`func (o *VerificationServiceErrorDetail) GetHintOk() (*string, bool)`

GetHintOk returns a tuple with the Hint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHint

`func (o *VerificationServiceErrorDetail) SetHint(v string)`

SetHint sets Hint field to given value.

### HasHint

`func (o *VerificationServiceErrorDetail) HasHint() bool`

HasHint returns a boolean if a field has been set.

### SetHintNil

`func (o *VerificationServiceErrorDetail) SetHintNil(b bool)`

 SetHintNil sets the value for Hint to be an explicit nil

### UnsetHint
`func (o *VerificationServiceErrorDetail) UnsetHint()`

UnsetHint ensures that no value is present for Hint, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


