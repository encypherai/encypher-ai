# C2PAAssertionValidateResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** |  | 
**Assertions** | [**[]C2PAAssertionValidationResult**](C2PAAssertionValidationResult.md) |  | 

## Methods

### NewC2PAAssertionValidateResponse

`func NewC2PAAssertionValidateResponse(valid bool, assertions []C2PAAssertionValidationResult, ) *C2PAAssertionValidateResponse`

NewC2PAAssertionValidateResponse instantiates a new C2PAAssertionValidateResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PAAssertionValidateResponseWithDefaults

`func NewC2PAAssertionValidateResponseWithDefaults() *C2PAAssertionValidateResponse`

NewC2PAAssertionValidateResponseWithDefaults instantiates a new C2PAAssertionValidateResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *C2PAAssertionValidateResponse) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *C2PAAssertionValidateResponse) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *C2PAAssertionValidateResponse) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetAssertions

`func (o *C2PAAssertionValidateResponse) GetAssertions() []C2PAAssertionValidationResult`

GetAssertions returns the Assertions field if non-nil, zero value otherwise.

### GetAssertionsOk

`func (o *C2PAAssertionValidateResponse) GetAssertionsOk() (*[]C2PAAssertionValidationResult, bool)`

GetAssertionsOk returns a tuple with the Assertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAssertions

`func (o *C2PAAssertionValidateResponse) SetAssertions(v []C2PAAssertionValidationResult)`

SetAssertions sets Assertions field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


