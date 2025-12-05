# LookupRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SentenceText** | **string** | Sentence to look up | 

## Methods

### NewLookupRequest

`func NewLookupRequest(sentenceText string, ) *LookupRequest`

NewLookupRequest instantiates a new LookupRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLookupRequestWithDefaults

`func NewLookupRequestWithDefaults() *LookupRequest`

NewLookupRequestWithDefaults instantiates a new LookupRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSentenceText

`func (o *LookupRequest) GetSentenceText() string`

GetSentenceText returns the SentenceText field if non-nil, zero value otherwise.

### GetSentenceTextOk

`func (o *LookupRequest) GetSentenceTextOk() (*string, bool)`

GetSentenceTextOk returns a tuple with the SentenceText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSentenceText

`func (o *LookupRequest) SetSentenceText(v string)`

SetSentenceText sets SentenceText field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


