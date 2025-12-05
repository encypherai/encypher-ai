# C2PAAssertionValidateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Label** | **string** | Assertion label to validate | 
**Data** | **map[string]interface{}** | Assertion data to validate | 

## Methods

### NewC2PAAssertionValidateRequest

`func NewC2PAAssertionValidateRequest(label string, data map[string]interface{}, ) *C2PAAssertionValidateRequest`

NewC2PAAssertionValidateRequest instantiates a new C2PAAssertionValidateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PAAssertionValidateRequestWithDefaults

`func NewC2PAAssertionValidateRequestWithDefaults() *C2PAAssertionValidateRequest`

NewC2PAAssertionValidateRequestWithDefaults instantiates a new C2PAAssertionValidateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetLabel

`func (o *C2PAAssertionValidateRequest) GetLabel() string`

GetLabel returns the Label field if non-nil, zero value otherwise.

### GetLabelOk

`func (o *C2PAAssertionValidateRequest) GetLabelOk() (*string, bool)`

GetLabelOk returns a tuple with the Label field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLabel

`func (o *C2PAAssertionValidateRequest) SetLabel(v string)`

SetLabel sets Label field to given value.


### GetData

`func (o *C2PAAssertionValidateRequest) GetData() map[string]interface{}`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *C2PAAssertionValidateRequest) GetDataOk() (*map[string]interface{}, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *C2PAAssertionValidateRequest) SetData(v map[string]interface{})`

SetData sets Data field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


