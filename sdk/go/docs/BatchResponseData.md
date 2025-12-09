# BatchResponseData

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Results** | [**[]BatchItemResult**](BatchItemResult.md) | Per-item results | 
**Summary** | [**BatchSummary**](BatchSummary.md) | Aggregate stats for the batch | 

## Methods

### NewBatchResponseData

`func NewBatchResponseData(results []BatchItemResult, summary BatchSummary, ) *BatchResponseData`

NewBatchResponseData instantiates a new BatchResponseData object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchResponseDataWithDefaults

`func NewBatchResponseDataWithDefaults() *BatchResponseData`

NewBatchResponseDataWithDefaults instantiates a new BatchResponseData object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetResults

`func (o *BatchResponseData) GetResults() []BatchItemResult`

GetResults returns the Results field if non-nil, zero value otherwise.

### GetResultsOk

`func (o *BatchResponseData) GetResultsOk() (*[]BatchItemResult, bool)`

GetResultsOk returns a tuple with the Results field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResults

`func (o *BatchResponseData) SetResults(v []BatchItemResult)`

SetResults sets Results field to given value.


### GetSummary

`func (o *BatchResponseData) GetSummary() BatchSummary`

GetSummary returns the Summary field if non-nil, zero value otherwise.

### GetSummaryOk

`func (o *BatchResponseData) GetSummaryOk() (*BatchSummary, bool)`

GetSummaryOk returns a tuple with the Summary field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSummary

`func (o *BatchResponseData) SetSummary(v BatchSummary)`

SetSummary sets Summary field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


