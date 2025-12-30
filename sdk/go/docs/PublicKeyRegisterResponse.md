# PublicKeyRegisterResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Data** | Pointer to [**NullablePublicKeyInfo**](PublicKeyInfo.md) |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewPublicKeyRegisterResponse

`func NewPublicKeyRegisterResponse() *PublicKeyRegisterResponse`

NewPublicKeyRegisterResponse instantiates a new PublicKeyRegisterResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPublicKeyRegisterResponseWithDefaults

`func NewPublicKeyRegisterResponseWithDefaults() *PublicKeyRegisterResponse`

NewPublicKeyRegisterResponseWithDefaults instantiates a new PublicKeyRegisterResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *PublicKeyRegisterResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *PublicKeyRegisterResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *PublicKeyRegisterResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *PublicKeyRegisterResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetData

`func (o *PublicKeyRegisterResponse) GetData() PublicKeyInfo`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *PublicKeyRegisterResponse) GetDataOk() (*PublicKeyInfo, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *PublicKeyRegisterResponse) SetData(v PublicKeyInfo)`

SetData sets Data field to given value.

### HasData

`func (o *PublicKeyRegisterResponse) HasData() bool`

HasData returns a boolean if a field has been set.

### SetDataNil

`func (o *PublicKeyRegisterResponse) SetDataNil(b bool)`

 SetDataNil sets the value for Data to be an explicit nil

### UnsetData
`func (o *PublicKeyRegisterResponse) UnsetData()`

UnsetData ensures that no value is present for Data, not even an explicit nil
### GetError

`func (o *PublicKeyRegisterResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *PublicKeyRegisterResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *PublicKeyRegisterResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *PublicKeyRegisterResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *PublicKeyRegisterResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *PublicKeyRegisterResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


