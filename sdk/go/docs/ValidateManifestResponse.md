# ValidateManifestResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** |  | 
**Errors** | Pointer to **[]string** |  | [optional] 
**Warnings** | Pointer to **[]string** |  | [optional] 
**Assertions** | Pointer to [**[]C2PAAssertionValidationResult**](C2PAAssertionValidationResult.md) |  | [optional] 

## Methods

### NewValidateManifestResponse

`func NewValidateManifestResponse(valid bool, ) *ValidateManifestResponse`

NewValidateManifestResponse instantiates a new ValidateManifestResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewValidateManifestResponseWithDefaults

`func NewValidateManifestResponseWithDefaults() *ValidateManifestResponse`

NewValidateManifestResponseWithDefaults instantiates a new ValidateManifestResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *ValidateManifestResponse) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *ValidateManifestResponse) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *ValidateManifestResponse) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetErrors

`func (o *ValidateManifestResponse) GetErrors() []string`

GetErrors returns the Errors field if non-nil, zero value otherwise.

### GetErrorsOk

`func (o *ValidateManifestResponse) GetErrorsOk() (*[]string, bool)`

GetErrorsOk returns a tuple with the Errors field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetErrors

`func (o *ValidateManifestResponse) SetErrors(v []string)`

SetErrors sets Errors field to given value.

### HasErrors

`func (o *ValidateManifestResponse) HasErrors() bool`

HasErrors returns a boolean if a field has been set.

### GetWarnings

`func (o *ValidateManifestResponse) GetWarnings() []string`

GetWarnings returns the Warnings field if non-nil, zero value otherwise.

### GetWarningsOk

`func (o *ValidateManifestResponse) GetWarningsOk() (*[]string, bool)`

GetWarningsOk returns a tuple with the Warnings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWarnings

`func (o *ValidateManifestResponse) SetWarnings(v []string)`

SetWarnings sets Warnings field to given value.

### HasWarnings

`func (o *ValidateManifestResponse) HasWarnings() bool`

HasWarnings returns a boolean if a field has been set.

### GetAssertions

`func (o *ValidateManifestResponse) GetAssertions() []C2PAAssertionValidationResult`

GetAssertions returns the Assertions field if non-nil, zero value otherwise.

### GetAssertionsOk

`func (o *ValidateManifestResponse) GetAssertionsOk() (*[]C2PAAssertionValidationResult, bool)`

GetAssertionsOk returns a tuple with the Assertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAssertions

`func (o *ValidateManifestResponse) SetAssertions(v []C2PAAssertionValidationResult)`

SetAssertions sets Assertions field to given value.

### HasAssertions

`func (o *ValidateManifestResponse) HasAssertions() bool`

HasAssertions returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


