# AppSchemasMerkleErrorResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** | Always false for errors | [optional] [default to false]
**Error** | **string** | Error type | 
**Message** | **string** | Human-readable error message | 
**Details** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewAppSchemasMerkleErrorResponse

`func NewAppSchemasMerkleErrorResponse(error_ string, message string, ) *AppSchemasMerkleErrorResponse`

NewAppSchemasMerkleErrorResponse instantiates a new AppSchemasMerkleErrorResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSchemasMerkleErrorResponseWithDefaults

`func NewAppSchemasMerkleErrorResponseWithDefaults() *AppSchemasMerkleErrorResponse`

NewAppSchemasMerkleErrorResponseWithDefaults instantiates a new AppSchemasMerkleErrorResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *AppSchemasMerkleErrorResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *AppSchemasMerkleErrorResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *AppSchemasMerkleErrorResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *AppSchemasMerkleErrorResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetError

`func (o *AppSchemasMerkleErrorResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *AppSchemasMerkleErrorResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *AppSchemasMerkleErrorResponse) SetError(v string)`

SetError sets Error field to given value.


### GetMessage

`func (o *AppSchemasMerkleErrorResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *AppSchemasMerkleErrorResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *AppSchemasMerkleErrorResponse) SetMessage(v string)`

SetMessage sets Message field to given value.


### GetDetails

`func (o *AppSchemasMerkleErrorResponse) GetDetails() map[string]interface{}`

GetDetails returns the Details field if non-nil, zero value otherwise.

### GetDetailsOk

`func (o *AppSchemasMerkleErrorResponse) GetDetailsOk() (*map[string]interface{}, bool)`

GetDetailsOk returns a tuple with the Details field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetails

`func (o *AppSchemasMerkleErrorResponse) SetDetails(v map[string]interface{})`

SetDetails sets Details field to given value.

### HasDetails

`func (o *AppSchemasMerkleErrorResponse) HasDetails() bool`

HasDetails returns a boolean if a field has been set.

### SetDetailsNil

`func (o *AppSchemasMerkleErrorResponse) SetDetailsNil(b bool)`

 SetDetailsNil sets the value for Details to be an explicit nil

### UnsetDetails
`func (o *AppSchemasMerkleErrorResponse) UnsetDetails()`

UnsetDetails ensures that no value is present for Details, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


