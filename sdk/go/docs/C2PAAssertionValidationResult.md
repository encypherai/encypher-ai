# C2PAAssertionValidationResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Label** | **string** |  | 
**Valid** | **bool** |  | 
**Errors** | Pointer to **[]string** |  | [optional] 
**Warnings** | Pointer to **[]string** |  | [optional] 

## Methods

### NewC2PAAssertionValidationResult

`func NewC2PAAssertionValidationResult(label string, valid bool, ) *C2PAAssertionValidationResult`

NewC2PAAssertionValidationResult instantiates a new C2PAAssertionValidationResult object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PAAssertionValidationResultWithDefaults

`func NewC2PAAssertionValidationResultWithDefaults() *C2PAAssertionValidationResult`

NewC2PAAssertionValidationResultWithDefaults instantiates a new C2PAAssertionValidationResult object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetLabel

`func (o *C2PAAssertionValidationResult) GetLabel() string`

GetLabel returns the Label field if non-nil, zero value otherwise.

### GetLabelOk

`func (o *C2PAAssertionValidationResult) GetLabelOk() (*string, bool)`

GetLabelOk returns a tuple with the Label field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLabel

`func (o *C2PAAssertionValidationResult) SetLabel(v string)`

SetLabel sets Label field to given value.


### GetValid

`func (o *C2PAAssertionValidationResult) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *C2PAAssertionValidationResult) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *C2PAAssertionValidationResult) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetErrors

`func (o *C2PAAssertionValidationResult) GetErrors() []string`

GetErrors returns the Errors field if non-nil, zero value otherwise.

### GetErrorsOk

`func (o *C2PAAssertionValidationResult) GetErrorsOk() (*[]string, bool)`

GetErrorsOk returns a tuple with the Errors field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetErrors

`func (o *C2PAAssertionValidationResult) SetErrors(v []string)`

SetErrors sets Errors field to given value.

### HasErrors

`func (o *C2PAAssertionValidationResult) HasErrors() bool`

HasErrors returns a boolean if a field has been set.

### GetWarnings

`func (o *C2PAAssertionValidationResult) GetWarnings() []string`

GetWarnings returns the Warnings field if non-nil, zero value otherwise.

### GetWarningsOk

`func (o *C2PAAssertionValidationResult) GetWarningsOk() (*[]string, bool)`

GetWarningsOk returns a tuple with the Warnings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWarnings

`func (o *C2PAAssertionValidationResult) SetWarnings(v []string)`

SetWarnings sets Warnings field to given value.

### HasWarnings

`func (o *C2PAAssertionValidationResult) HasWarnings() bool`

HasWarnings returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


