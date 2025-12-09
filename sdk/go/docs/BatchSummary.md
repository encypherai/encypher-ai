# BatchSummary

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TotalItems** | **int32** | Total number of documents in the batch | 
**SuccessCount** | **int32** | How many items succeeded | 
**FailureCount** | **int32** | How many items failed | 
**Mode** | **string** | Batch mode | 
**Status** | **string** | Batch lifecycle status | 
**DurationMs** | **int32** | Total processing time for the batch | 
**StartedAt** | Pointer to **NullableString** |  | [optional] 
**CompletedAt** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewBatchSummary

`func NewBatchSummary(totalItems int32, successCount int32, failureCount int32, mode string, status string, durationMs int32, ) *BatchSummary`

NewBatchSummary instantiates a new BatchSummary object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchSummaryWithDefaults

`func NewBatchSummaryWithDefaults() *BatchSummary`

NewBatchSummaryWithDefaults instantiates a new BatchSummary object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTotalItems

`func (o *BatchSummary) GetTotalItems() int32`

GetTotalItems returns the TotalItems field if non-nil, zero value otherwise.

### GetTotalItemsOk

`func (o *BatchSummary) GetTotalItemsOk() (*int32, bool)`

GetTotalItemsOk returns a tuple with the TotalItems field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalItems

`func (o *BatchSummary) SetTotalItems(v int32)`

SetTotalItems sets TotalItems field to given value.


### GetSuccessCount

`func (o *BatchSummary) GetSuccessCount() int32`

GetSuccessCount returns the SuccessCount field if non-nil, zero value otherwise.

### GetSuccessCountOk

`func (o *BatchSummary) GetSuccessCountOk() (*int32, bool)`

GetSuccessCountOk returns a tuple with the SuccessCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccessCount

`func (o *BatchSummary) SetSuccessCount(v int32)`

SetSuccessCount sets SuccessCount field to given value.


### GetFailureCount

`func (o *BatchSummary) GetFailureCount() int32`

GetFailureCount returns the FailureCount field if non-nil, zero value otherwise.

### GetFailureCountOk

`func (o *BatchSummary) GetFailureCountOk() (*int32, bool)`

GetFailureCountOk returns a tuple with the FailureCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFailureCount

`func (o *BatchSummary) SetFailureCount(v int32)`

SetFailureCount sets FailureCount field to given value.


### GetMode

`func (o *BatchSummary) GetMode() string`

GetMode returns the Mode field if non-nil, zero value otherwise.

### GetModeOk

`func (o *BatchSummary) GetModeOk() (*string, bool)`

GetModeOk returns a tuple with the Mode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMode

`func (o *BatchSummary) SetMode(v string)`

SetMode sets Mode field to given value.


### GetStatus

`func (o *BatchSummary) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *BatchSummary) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *BatchSummary) SetStatus(v string)`

SetStatus sets Status field to given value.


### GetDurationMs

`func (o *BatchSummary) GetDurationMs() int32`

GetDurationMs returns the DurationMs field if non-nil, zero value otherwise.

### GetDurationMsOk

`func (o *BatchSummary) GetDurationMsOk() (*int32, bool)`

GetDurationMsOk returns a tuple with the DurationMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDurationMs

`func (o *BatchSummary) SetDurationMs(v int32)`

SetDurationMs sets DurationMs field to given value.


### GetStartedAt

`func (o *BatchSummary) GetStartedAt() string`

GetStartedAt returns the StartedAt field if non-nil, zero value otherwise.

### GetStartedAtOk

`func (o *BatchSummary) GetStartedAtOk() (*string, bool)`

GetStartedAtOk returns a tuple with the StartedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStartedAt

`func (o *BatchSummary) SetStartedAt(v string)`

SetStartedAt sets StartedAt field to given value.

### HasStartedAt

`func (o *BatchSummary) HasStartedAt() bool`

HasStartedAt returns a boolean if a field has been set.

### SetStartedAtNil

`func (o *BatchSummary) SetStartedAtNil(b bool)`

 SetStartedAtNil sets the value for StartedAt to be an explicit nil

### UnsetStartedAt
`func (o *BatchSummary) UnsetStartedAt()`

UnsetStartedAt ensures that no value is present for StartedAt, not even an explicit nil
### GetCompletedAt

`func (o *BatchSummary) GetCompletedAt() string`

GetCompletedAt returns the CompletedAt field if non-nil, zero value otherwise.

### GetCompletedAtOk

`func (o *BatchSummary) GetCompletedAtOk() (*string, bool)`

GetCompletedAtOk returns a tuple with the CompletedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCompletedAt

`func (o *BatchSummary) SetCompletedAt(v string)`

SetCompletedAt sets CompletedAt field to given value.

### HasCompletedAt

`func (o *BatchSummary) HasCompletedAt() bool`

HasCompletedAt returns a boolean if a field has been set.

### SetCompletedAtNil

`func (o *BatchSummary) SetCompletedAtNil(b bool)`

 SetCompletedAtNil sets the value for CompletedAt to be an explicit nil

### UnsetCompletedAt
`func (o *BatchSummary) UnsetCompletedAt()`

UnsetCompletedAt ensures that no value is present for CompletedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


