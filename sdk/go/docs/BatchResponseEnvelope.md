# BatchResponseEnvelope

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Indicates whether the batch request succeeded | 
**BatchId** | **string** | Batch request identifier | 
**Data** | Pointer to [**NullableBatchResponseData**](BatchResponseData.md) |  | [optional] 
**Error** | Pointer to [**NullableErrorDetail**](ErrorDetail.md) |  | [optional] 
**CorrelationId** | **string** | Request correlation identifier for tracing | 

## Methods

### NewBatchResponseEnvelope

`func NewBatchResponseEnvelope(success bool, batchId string, correlationId string, ) *BatchResponseEnvelope`

NewBatchResponseEnvelope instantiates a new BatchResponseEnvelope object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchResponseEnvelopeWithDefaults

`func NewBatchResponseEnvelopeWithDefaults() *BatchResponseEnvelope`

NewBatchResponseEnvelopeWithDefaults instantiates a new BatchResponseEnvelope object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *BatchResponseEnvelope) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *BatchResponseEnvelope) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *BatchResponseEnvelope) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetBatchId

`func (o *BatchResponseEnvelope) GetBatchId() string`

GetBatchId returns the BatchId field if non-nil, zero value otherwise.

### GetBatchIdOk

`func (o *BatchResponseEnvelope) GetBatchIdOk() (*string, bool)`

GetBatchIdOk returns a tuple with the BatchId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBatchId

`func (o *BatchResponseEnvelope) SetBatchId(v string)`

SetBatchId sets BatchId field to given value.


### GetData

`func (o *BatchResponseEnvelope) GetData() BatchResponseData`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *BatchResponseEnvelope) GetDataOk() (*BatchResponseData, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *BatchResponseEnvelope) SetData(v BatchResponseData)`

SetData sets Data field to given value.

### HasData

`func (o *BatchResponseEnvelope) HasData() bool`

HasData returns a boolean if a field has been set.

### SetDataNil

`func (o *BatchResponseEnvelope) SetDataNil(b bool)`

 SetDataNil sets the value for Data to be an explicit nil

### UnsetData
`func (o *BatchResponseEnvelope) UnsetData()`

UnsetData ensures that no value is present for Data, not even an explicit nil
### GetError

`func (o *BatchResponseEnvelope) GetError() ErrorDetail`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *BatchResponseEnvelope) GetErrorOk() (*ErrorDetail, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *BatchResponseEnvelope) SetError(v ErrorDetail)`

SetError sets Error field to given value.

### HasError

`func (o *BatchResponseEnvelope) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *BatchResponseEnvelope) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *BatchResponseEnvelope) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil
### GetCorrelationId

`func (o *BatchResponseEnvelope) GetCorrelationId() string`

GetCorrelationId returns the CorrelationId field if non-nil, zero value otherwise.

### GetCorrelationIdOk

`func (o *BatchResponseEnvelope) GetCorrelationIdOk() (*string, bool)`

GetCorrelationIdOk returns a tuple with the CorrelationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCorrelationId

`func (o *BatchResponseEnvelope) SetCorrelationId(v string)`

SetCorrelationId sets CorrelationId field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


