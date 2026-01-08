# KeyCreateResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Data** | **map[string]interface{}** |  | 
**Warning** | Pointer to **string** |  | [optional] [default to "Store this key securely. It will not be shown again."]

## Methods

### NewKeyCreateResponse

`func NewKeyCreateResponse(data map[string]interface{}, ) *KeyCreateResponse`

NewKeyCreateResponse instantiates a new KeyCreateResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewKeyCreateResponseWithDefaults

`func NewKeyCreateResponseWithDefaults() *KeyCreateResponse`

NewKeyCreateResponseWithDefaults instantiates a new KeyCreateResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *KeyCreateResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *KeyCreateResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *KeyCreateResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *KeyCreateResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetData

`func (o *KeyCreateResponse) GetData() map[string]interface{}`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *KeyCreateResponse) GetDataOk() (*map[string]interface{}, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *KeyCreateResponse) SetData(v map[string]interface{})`

SetData sets Data field to given value.


### GetWarning

`func (o *KeyCreateResponse) GetWarning() string`

GetWarning returns the Warning field if non-nil, zero value otherwise.

### GetWarningOk

`func (o *KeyCreateResponse) GetWarningOk() (*string, bool)`

GetWarningOk returns a tuple with the Warning field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWarning

`func (o *KeyCreateResponse) SetWarning(v string)`

SetWarning sets Warning field to given value.

### HasWarning

`func (o *KeyCreateResponse) HasWarning() bool`

HasWarning returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


