# EmbeddingResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Index** | **int32** | Index of this embedding (0-based) | 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**VerificationStatus** | Pointer to **string** |  | [optional] [default to "Not Attempted"]
**Error** | Pointer to **NullableString** |  | [optional] 
**Verdict** | Pointer to [**NullableAppRoutersToolsVerifyVerdict**](AppRoutersToolsVerifyVerdict.md) |  | [optional] 
**TextSpan** | Pointer to **[]interface{}** |  | [optional] 
**CleanText** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewEmbeddingResult

`func NewEmbeddingResult(index int32, ) *EmbeddingResult`

NewEmbeddingResult instantiates a new EmbeddingResult object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEmbeddingResultWithDefaults

`func NewEmbeddingResultWithDefaults() *EmbeddingResult`

NewEmbeddingResultWithDefaults instantiates a new EmbeddingResult object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetIndex

`func (o *EmbeddingResult) GetIndex() int32`

GetIndex returns the Index field if non-nil, zero value otherwise.

### GetIndexOk

`func (o *EmbeddingResult) GetIndexOk() (*int32, bool)`

GetIndexOk returns a tuple with the Index field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIndex

`func (o *EmbeddingResult) SetIndex(v int32)`

SetIndex sets Index field to given value.


### GetMetadata

`func (o *EmbeddingResult) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *EmbeddingResult) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *EmbeddingResult) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *EmbeddingResult) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *EmbeddingResult) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *EmbeddingResult) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetVerificationStatus

`func (o *EmbeddingResult) GetVerificationStatus() string`

GetVerificationStatus returns the VerificationStatus field if non-nil, zero value otherwise.

### GetVerificationStatusOk

`func (o *EmbeddingResult) GetVerificationStatusOk() (*string, bool)`

GetVerificationStatusOk returns a tuple with the VerificationStatus field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationStatus

`func (o *EmbeddingResult) SetVerificationStatus(v string)`

SetVerificationStatus sets VerificationStatus field to given value.

### HasVerificationStatus

`func (o *EmbeddingResult) HasVerificationStatus() bool`

HasVerificationStatus returns a boolean if a field has been set.

### GetError

`func (o *EmbeddingResult) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *EmbeddingResult) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *EmbeddingResult) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *EmbeddingResult) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *EmbeddingResult) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *EmbeddingResult) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil
### GetVerdict

`func (o *EmbeddingResult) GetVerdict() AppRoutersToolsVerifyVerdict`

GetVerdict returns the Verdict field if non-nil, zero value otherwise.

### GetVerdictOk

`func (o *EmbeddingResult) GetVerdictOk() (*AppRoutersToolsVerifyVerdict, bool)`

GetVerdictOk returns a tuple with the Verdict field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerdict

`func (o *EmbeddingResult) SetVerdict(v AppRoutersToolsVerifyVerdict)`

SetVerdict sets Verdict field to given value.

### HasVerdict

`func (o *EmbeddingResult) HasVerdict() bool`

HasVerdict returns a boolean if a field has been set.

### SetVerdictNil

`func (o *EmbeddingResult) SetVerdictNil(b bool)`

 SetVerdictNil sets the value for Verdict to be an explicit nil

### UnsetVerdict
`func (o *EmbeddingResult) UnsetVerdict()`

UnsetVerdict ensures that no value is present for Verdict, not even an explicit nil
### GetTextSpan

`func (o *EmbeddingResult) GetTextSpan() []interface{}`

GetTextSpan returns the TextSpan field if non-nil, zero value otherwise.

### GetTextSpanOk

`func (o *EmbeddingResult) GetTextSpanOk() (*[]interface{}, bool)`

GetTextSpanOk returns a tuple with the TextSpan field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextSpan

`func (o *EmbeddingResult) SetTextSpan(v []interface{})`

SetTextSpan sets TextSpan field to given value.

### HasTextSpan

`func (o *EmbeddingResult) HasTextSpan() bool`

HasTextSpan returns a boolean if a field has been set.

### SetTextSpanNil

`func (o *EmbeddingResult) SetTextSpanNil(b bool)`

 SetTextSpanNil sets the value for TextSpan to be an explicit nil

### UnsetTextSpan
`func (o *EmbeddingResult) UnsetTextSpan()`

UnsetTextSpan ensures that no value is present for TextSpan, not even an explicit nil
### GetCleanText

`func (o *EmbeddingResult) GetCleanText() string`

GetCleanText returns the CleanText field if non-nil, zero value otherwise.

### GetCleanTextOk

`func (o *EmbeddingResult) GetCleanTextOk() (*string, bool)`

GetCleanTextOk returns a tuple with the CleanText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCleanText

`func (o *EmbeddingResult) SetCleanText(v string)`

SetCleanText sets CleanText field to given value.

### HasCleanText

`func (o *EmbeddingResult) HasCleanText() bool`

HasCleanText returns a boolean if a field has been set.

### SetCleanTextNil

`func (o *EmbeddingResult) SetCleanTextNil(b bool)`

 SetCleanTextNil sets the value for CleanText to be an explicit nil

### UnsetCleanText
`func (o *EmbeddingResult) UnsetCleanText()`

UnsetCleanText ensures that no value is present for CleanText, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


