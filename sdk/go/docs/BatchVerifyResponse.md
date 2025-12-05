# BatchVerifyResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Results** | [**[]BatchVerifyResult**](BatchVerifyResult.md) | Verification results | 
**Total** | **int32** | Total number of embeddings checked | 
**ValidCount** | **int32** | Number of valid embeddings | 
**InvalidCount** | **int32** | Number of invalid embeddings | 

## Methods

### NewBatchVerifyResponse

`func NewBatchVerifyResponse(results []BatchVerifyResult, total int32, validCount int32, invalidCount int32, ) *BatchVerifyResponse`

NewBatchVerifyResponse instantiates a new BatchVerifyResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchVerifyResponseWithDefaults

`func NewBatchVerifyResponseWithDefaults() *BatchVerifyResponse`

NewBatchVerifyResponseWithDefaults instantiates a new BatchVerifyResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetResults

`func (o *BatchVerifyResponse) GetResults() []BatchVerifyResult`

GetResults returns the Results field if non-nil, zero value otherwise.

### GetResultsOk

`func (o *BatchVerifyResponse) GetResultsOk() (*[]BatchVerifyResult, bool)`

GetResultsOk returns a tuple with the Results field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResults

`func (o *BatchVerifyResponse) SetResults(v []BatchVerifyResult)`

SetResults sets Results field to given value.


### GetTotal

`func (o *BatchVerifyResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *BatchVerifyResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *BatchVerifyResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetValidCount

`func (o *BatchVerifyResponse) GetValidCount() int32`

GetValidCount returns the ValidCount field if non-nil, zero value otherwise.

### GetValidCountOk

`func (o *BatchVerifyResponse) GetValidCountOk() (*int32, bool)`

GetValidCountOk returns a tuple with the ValidCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidCount

`func (o *BatchVerifyResponse) SetValidCount(v int32)`

SetValidCount sets ValidCount field to given value.


### GetInvalidCount

`func (o *BatchVerifyResponse) GetInvalidCount() int32`

GetInvalidCount returns the InvalidCount field if non-nil, zero value otherwise.

### GetInvalidCountOk

`func (o *BatchVerifyResponse) GetInvalidCountOk() (*int32, bool)`

GetInvalidCountOk returns a tuple with the InvalidCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInvalidCount

`func (o *BatchVerifyResponse) SetInvalidCount(v int32)`

SetInvalidCount sets InvalidCount field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


