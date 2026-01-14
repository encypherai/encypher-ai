# VerifyResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** |  | 
**Data** | Pointer to [**NullableVerifyVerdict**](VerifyVerdict.md) |  | [optional] 
**Error** | Pointer to [**NullableErrorDetail**](ErrorDetail.md) |  | [optional] 
**CorrelationId** | **string** |  | 

## Methods

### NewVerifyResponse

`func NewVerifyResponse(success bool, correlationId string, ) *VerifyResponse`

NewVerifyResponse instantiates a new VerifyResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyResponseWithDefaults

`func NewVerifyResponseWithDefaults() *VerifyResponse`

NewVerifyResponseWithDefaults instantiates a new VerifyResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *VerifyResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *VerifyResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *VerifyResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetData

`func (o *VerifyResponse) GetData() VerifyVerdict`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *VerifyResponse) GetDataOk() (*VerifyVerdict, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *VerifyResponse) SetData(v VerifyVerdict)`

SetData sets Data field to given value.

### HasData

`func (o *VerifyResponse) HasData() bool`

HasData returns a boolean if a field has been set.

### SetDataNil

`func (o *VerifyResponse) SetDataNil(b bool)`

 SetDataNil sets the value for Data to be an explicit nil

### UnsetData
`func (o *VerifyResponse) UnsetData()`

UnsetData ensures that no value is present for Data, not even an explicit nil
### GetError

`func (o *VerifyResponse) GetError() ErrorDetail`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *VerifyResponse) GetErrorOk() (*ErrorDetail, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *VerifyResponse) SetError(v ErrorDetail)`

SetError sets Error field to given value.

### HasError

`func (o *VerifyResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *VerifyResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *VerifyResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil
### GetCorrelationId

`func (o *VerifyResponse) GetCorrelationId() string`

GetCorrelationId returns the CorrelationId field if non-nil, zero value otherwise.

### GetCorrelationIdOk

`func (o *VerifyResponse) GetCorrelationIdOk() (*string, bool)`

GetCorrelationIdOk returns a tuple with the CorrelationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCorrelationId

`func (o *VerifyResponse) SetCorrelationId(v string)`

SetCorrelationId sets CorrelationId field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


