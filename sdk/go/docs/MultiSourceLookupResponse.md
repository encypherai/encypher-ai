# MultiSourceLookupResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether lookup succeeded | 
**QueryHash** | **string** | Hash of the queried text | 
**TotalSources** | **int32** | Total number of matching sources | 
**Sources** | Pointer to [**[]SourceRecord**](SourceRecord.md) | List of matching sources | [optional] 
**OriginalSource** | Pointer to [**NullableSourceRecord**](SourceRecord.md) |  | [optional] 
**HasChain** | **bool** | Whether sources form a linked chain | 
**ChainLength** | Pointer to **int32** | Length of the source chain | [optional] [default to 0]
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 
**Message** | **string** | Status message | 

## Methods

### NewMultiSourceLookupResponse

`func NewMultiSourceLookupResponse(success bool, queryHash string, totalSources int32, hasChain bool, processingTimeMs float32, message string, ) *MultiSourceLookupResponse`

NewMultiSourceLookupResponse instantiates a new MultiSourceLookupResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiSourceLookupResponseWithDefaults

`func NewMultiSourceLookupResponseWithDefaults() *MultiSourceLookupResponse`

NewMultiSourceLookupResponseWithDefaults instantiates a new MultiSourceLookupResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *MultiSourceLookupResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *MultiSourceLookupResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *MultiSourceLookupResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetQueryHash

`func (o *MultiSourceLookupResponse) GetQueryHash() string`

GetQueryHash returns the QueryHash field if non-nil, zero value otherwise.

### GetQueryHashOk

`func (o *MultiSourceLookupResponse) GetQueryHashOk() (*string, bool)`

GetQueryHashOk returns a tuple with the QueryHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetQueryHash

`func (o *MultiSourceLookupResponse) SetQueryHash(v string)`

SetQueryHash sets QueryHash field to given value.


### GetTotalSources

`func (o *MultiSourceLookupResponse) GetTotalSources() int32`

GetTotalSources returns the TotalSources field if non-nil, zero value otherwise.

### GetTotalSourcesOk

`func (o *MultiSourceLookupResponse) GetTotalSourcesOk() (*int32, bool)`

GetTotalSourcesOk returns a tuple with the TotalSources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSources

`func (o *MultiSourceLookupResponse) SetTotalSources(v int32)`

SetTotalSources sets TotalSources field to given value.


### GetSources

`func (o *MultiSourceLookupResponse) GetSources() []SourceRecord`

GetSources returns the Sources field if non-nil, zero value otherwise.

### GetSourcesOk

`func (o *MultiSourceLookupResponse) GetSourcesOk() (*[]SourceRecord, bool)`

GetSourcesOk returns a tuple with the Sources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSources

`func (o *MultiSourceLookupResponse) SetSources(v []SourceRecord)`

SetSources sets Sources field to given value.

### HasSources

`func (o *MultiSourceLookupResponse) HasSources() bool`

HasSources returns a boolean if a field has been set.

### GetOriginalSource

`func (o *MultiSourceLookupResponse) GetOriginalSource() SourceRecord`

GetOriginalSource returns the OriginalSource field if non-nil, zero value otherwise.

### GetOriginalSourceOk

`func (o *MultiSourceLookupResponse) GetOriginalSourceOk() (*SourceRecord, bool)`

GetOriginalSourceOk returns a tuple with the OriginalSource field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOriginalSource

`func (o *MultiSourceLookupResponse) SetOriginalSource(v SourceRecord)`

SetOriginalSource sets OriginalSource field to given value.

### HasOriginalSource

`func (o *MultiSourceLookupResponse) HasOriginalSource() bool`

HasOriginalSource returns a boolean if a field has been set.

### SetOriginalSourceNil

`func (o *MultiSourceLookupResponse) SetOriginalSourceNil(b bool)`

 SetOriginalSourceNil sets the value for OriginalSource to be an explicit nil

### UnsetOriginalSource
`func (o *MultiSourceLookupResponse) UnsetOriginalSource()`

UnsetOriginalSource ensures that no value is present for OriginalSource, not even an explicit nil
### GetHasChain

`func (o *MultiSourceLookupResponse) GetHasChain() bool`

GetHasChain returns the HasChain field if non-nil, zero value otherwise.

### GetHasChainOk

`func (o *MultiSourceLookupResponse) GetHasChainOk() (*bool, bool)`

GetHasChainOk returns a tuple with the HasChain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHasChain

`func (o *MultiSourceLookupResponse) SetHasChain(v bool)`

SetHasChain sets HasChain field to given value.


### GetChainLength

`func (o *MultiSourceLookupResponse) GetChainLength() int32`

GetChainLength returns the ChainLength field if non-nil, zero value otherwise.

### GetChainLengthOk

`func (o *MultiSourceLookupResponse) GetChainLengthOk() (*int32, bool)`

GetChainLengthOk returns a tuple with the ChainLength field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetChainLength

`func (o *MultiSourceLookupResponse) SetChainLength(v int32)`

SetChainLength sets ChainLength field to given value.

### HasChainLength

`func (o *MultiSourceLookupResponse) HasChainLength() bool`

HasChainLength returns a boolean if a field has been set.

### GetProcessingTimeMs

`func (o *MultiSourceLookupResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *MultiSourceLookupResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *MultiSourceLookupResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetMessage

`func (o *MultiSourceLookupResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *MultiSourceLookupResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *MultiSourceLookupResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


