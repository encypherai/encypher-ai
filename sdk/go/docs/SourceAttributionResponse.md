# SourceAttributionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether search was successful | 
**QueryHash** | **string** | Hash of the queried text segment | 
**MatchesFound** | **int32** | Number of matching sources found | 
**Sources** | [**[]SourceMatch**](SourceMatch.md) | List of matching sources | 
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 

## Methods

### NewSourceAttributionResponse

`func NewSourceAttributionResponse(success bool, queryHash string, matchesFound int32, sources []SourceMatch, processingTimeMs float32, ) *SourceAttributionResponse`

NewSourceAttributionResponse instantiates a new SourceAttributionResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSourceAttributionResponseWithDefaults

`func NewSourceAttributionResponseWithDefaults() *SourceAttributionResponse`

NewSourceAttributionResponseWithDefaults instantiates a new SourceAttributionResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *SourceAttributionResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *SourceAttributionResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *SourceAttributionResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetQueryHash

`func (o *SourceAttributionResponse) GetQueryHash() string`

GetQueryHash returns the QueryHash field if non-nil, zero value otherwise.

### GetQueryHashOk

`func (o *SourceAttributionResponse) GetQueryHashOk() (*string, bool)`

GetQueryHashOk returns a tuple with the QueryHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetQueryHash

`func (o *SourceAttributionResponse) SetQueryHash(v string)`

SetQueryHash sets QueryHash field to given value.


### GetMatchesFound

`func (o *SourceAttributionResponse) GetMatchesFound() int32`

GetMatchesFound returns the MatchesFound field if non-nil, zero value otherwise.

### GetMatchesFoundOk

`func (o *SourceAttributionResponse) GetMatchesFoundOk() (*int32, bool)`

GetMatchesFoundOk returns a tuple with the MatchesFound field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchesFound

`func (o *SourceAttributionResponse) SetMatchesFound(v int32)`

SetMatchesFound sets MatchesFound field to given value.


### GetSources

`func (o *SourceAttributionResponse) GetSources() []SourceMatch`

GetSources returns the Sources field if non-nil, zero value otherwise.

### GetSourcesOk

`func (o *SourceAttributionResponse) GetSourcesOk() (*[]SourceMatch, bool)`

GetSourcesOk returns a tuple with the Sources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSources

`func (o *SourceAttributionResponse) SetSources(v []SourceMatch)`

SetSources sets Sources field to given value.


### GetProcessingTimeMs

`func (o *SourceAttributionResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *SourceAttributionResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *SourceAttributionResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


