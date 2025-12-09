# VerifyRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | Text with embedded C2PA manifest | 

## Methods

### NewVerifyRequest

`func NewVerifyRequest(text string, ) *VerifyRequest`

NewVerifyRequest instantiates a new VerifyRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyRequestWithDefaults

`func NewVerifyRequestWithDefaults() *VerifyRequest`

NewVerifyRequestWithDefaults instantiates a new VerifyRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *VerifyRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *VerifyRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *VerifyRequest) SetText(v string)`

SetText sets Text field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


