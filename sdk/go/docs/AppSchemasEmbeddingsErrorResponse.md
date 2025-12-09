# AppSchemasEmbeddingsErrorResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** | Always false for errors | [optional] [default to false]
**Error** | **string** | Error message | 
**Detail** | Pointer to **NullableString** |  | [optional] 
**ErrorCode** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewAppSchemasEmbeddingsErrorResponse

`func NewAppSchemasEmbeddingsErrorResponse(error_ string, ) *AppSchemasEmbeddingsErrorResponse`

NewAppSchemasEmbeddingsErrorResponse instantiates a new AppSchemasEmbeddingsErrorResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSchemasEmbeddingsErrorResponseWithDefaults

`func NewAppSchemasEmbeddingsErrorResponseWithDefaults() *AppSchemasEmbeddingsErrorResponse`

NewAppSchemasEmbeddingsErrorResponseWithDefaults instantiates a new AppSchemasEmbeddingsErrorResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *AppSchemasEmbeddingsErrorResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *AppSchemasEmbeddingsErrorResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *AppSchemasEmbeddingsErrorResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *AppSchemasEmbeddingsErrorResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetError

`func (o *AppSchemasEmbeddingsErrorResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *AppSchemasEmbeddingsErrorResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *AppSchemasEmbeddingsErrorResponse) SetError(v string)`

SetError sets Error field to given value.


### GetDetail

`func (o *AppSchemasEmbeddingsErrorResponse) GetDetail() string`

GetDetail returns the Detail field if non-nil, zero value otherwise.

### GetDetailOk

`func (o *AppSchemasEmbeddingsErrorResponse) GetDetailOk() (*string, bool)`

GetDetailOk returns a tuple with the Detail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetail

`func (o *AppSchemasEmbeddingsErrorResponse) SetDetail(v string)`

SetDetail sets Detail field to given value.

### HasDetail

`func (o *AppSchemasEmbeddingsErrorResponse) HasDetail() bool`

HasDetail returns a boolean if a field has been set.

### SetDetailNil

`func (o *AppSchemasEmbeddingsErrorResponse) SetDetailNil(b bool)`

 SetDetailNil sets the value for Detail to be an explicit nil

### UnsetDetail
`func (o *AppSchemasEmbeddingsErrorResponse) UnsetDetail()`

UnsetDetail ensures that no value is present for Detail, not even an explicit nil
### GetErrorCode

`func (o *AppSchemasEmbeddingsErrorResponse) GetErrorCode() string`

GetErrorCode returns the ErrorCode field if non-nil, zero value otherwise.

### GetErrorCodeOk

`func (o *AppSchemasEmbeddingsErrorResponse) GetErrorCodeOk() (*string, bool)`

GetErrorCodeOk returns a tuple with the ErrorCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetErrorCode

`func (o *AppSchemasEmbeddingsErrorResponse) SetErrorCode(v string)`

SetErrorCode sets ErrorCode field to given value.

### HasErrorCode

`func (o *AppSchemasEmbeddingsErrorResponse) HasErrorCode() bool`

HasErrorCode returns a boolean if a field has been set.

### SetErrorCodeNil

`func (o *AppSchemasEmbeddingsErrorResponse) SetErrorCodeNil(b bool)`

 SetErrorCodeNil sets the value for ErrorCode to be an explicit nil

### UnsetErrorCode
`func (o *AppSchemasEmbeddingsErrorResponse) UnsetErrorCode()`

UnsetErrorCode ensures that no value is present for ErrorCode, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


