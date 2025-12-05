# BatchItemResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Document identifier from request | 
**Status** | **string** | Processing outcome for the document | 
**SignedText** | Pointer to **NullableString** |  | [optional] 
**EmbeddedContent** | Pointer to **NullableString** |  | [optional] 
**Verdict** | Pointer to [**NullableAppModelsResponseModelsVerifyVerdict**](AppModelsResponseModelsVerifyVerdict.md) |  | [optional] 
**ErrorCode** | Pointer to **NullableString** |  | [optional] 
**ErrorMessage** | Pointer to **NullableString** |  | [optional] 
**Statistics** | Pointer to **map[string]interface{}** | Timing and segmentation statistics for the item | [optional] 

## Methods

### NewBatchItemResult

`func NewBatchItemResult(documentId string, status string, ) *BatchItemResult`

NewBatchItemResult instantiates a new BatchItemResult object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchItemResultWithDefaults

`func NewBatchItemResultWithDefaults() *BatchItemResult`

NewBatchItemResultWithDefaults instantiates a new BatchItemResult object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *BatchItemResult) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *BatchItemResult) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *BatchItemResult) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetStatus

`func (o *BatchItemResult) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *BatchItemResult) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *BatchItemResult) SetStatus(v string)`

SetStatus sets Status field to given value.


### GetSignedText

`func (o *BatchItemResult) GetSignedText() string`

GetSignedText returns the SignedText field if non-nil, zero value otherwise.

### GetSignedTextOk

`func (o *BatchItemResult) GetSignedTextOk() (*string, bool)`

GetSignedTextOk returns a tuple with the SignedText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedText

`func (o *BatchItemResult) SetSignedText(v string)`

SetSignedText sets SignedText field to given value.

### HasSignedText

`func (o *BatchItemResult) HasSignedText() bool`

HasSignedText returns a boolean if a field has been set.

### SetSignedTextNil

`func (o *BatchItemResult) SetSignedTextNil(b bool)`

 SetSignedTextNil sets the value for SignedText to be an explicit nil

### UnsetSignedText
`func (o *BatchItemResult) UnsetSignedText()`

UnsetSignedText ensures that no value is present for SignedText, not even an explicit nil
### GetEmbeddedContent

`func (o *BatchItemResult) GetEmbeddedContent() string`

GetEmbeddedContent returns the EmbeddedContent field if non-nil, zero value otherwise.

### GetEmbeddedContentOk

`func (o *BatchItemResult) GetEmbeddedContentOk() (*string, bool)`

GetEmbeddedContentOk returns a tuple with the EmbeddedContent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddedContent

`func (o *BatchItemResult) SetEmbeddedContent(v string)`

SetEmbeddedContent sets EmbeddedContent field to given value.

### HasEmbeddedContent

`func (o *BatchItemResult) HasEmbeddedContent() bool`

HasEmbeddedContent returns a boolean if a field has been set.

### SetEmbeddedContentNil

`func (o *BatchItemResult) SetEmbeddedContentNil(b bool)`

 SetEmbeddedContentNil sets the value for EmbeddedContent to be an explicit nil

### UnsetEmbeddedContent
`func (o *BatchItemResult) UnsetEmbeddedContent()`

UnsetEmbeddedContent ensures that no value is present for EmbeddedContent, not even an explicit nil
### GetVerdict

`func (o *BatchItemResult) GetVerdict() AppModelsResponseModelsVerifyVerdict`

GetVerdict returns the Verdict field if non-nil, zero value otherwise.

### GetVerdictOk

`func (o *BatchItemResult) GetVerdictOk() (*AppModelsResponseModelsVerifyVerdict, bool)`

GetVerdictOk returns a tuple with the Verdict field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerdict

`func (o *BatchItemResult) SetVerdict(v AppModelsResponseModelsVerifyVerdict)`

SetVerdict sets Verdict field to given value.

### HasVerdict

`func (o *BatchItemResult) HasVerdict() bool`

HasVerdict returns a boolean if a field has been set.

### SetVerdictNil

`func (o *BatchItemResult) SetVerdictNil(b bool)`

 SetVerdictNil sets the value for Verdict to be an explicit nil

### UnsetVerdict
`func (o *BatchItemResult) UnsetVerdict()`

UnsetVerdict ensures that no value is present for Verdict, not even an explicit nil
### GetErrorCode

`func (o *BatchItemResult) GetErrorCode() string`

GetErrorCode returns the ErrorCode field if non-nil, zero value otherwise.

### GetErrorCodeOk

`func (o *BatchItemResult) GetErrorCodeOk() (*string, bool)`

GetErrorCodeOk returns a tuple with the ErrorCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetErrorCode

`func (o *BatchItemResult) SetErrorCode(v string)`

SetErrorCode sets ErrorCode field to given value.

### HasErrorCode

`func (o *BatchItemResult) HasErrorCode() bool`

HasErrorCode returns a boolean if a field has been set.

### SetErrorCodeNil

`func (o *BatchItemResult) SetErrorCodeNil(b bool)`

 SetErrorCodeNil sets the value for ErrorCode to be an explicit nil

### UnsetErrorCode
`func (o *BatchItemResult) UnsetErrorCode()`

UnsetErrorCode ensures that no value is present for ErrorCode, not even an explicit nil
### GetErrorMessage

`func (o *BatchItemResult) GetErrorMessage() string`

GetErrorMessage returns the ErrorMessage field if non-nil, zero value otherwise.

### GetErrorMessageOk

`func (o *BatchItemResult) GetErrorMessageOk() (*string, bool)`

GetErrorMessageOk returns a tuple with the ErrorMessage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetErrorMessage

`func (o *BatchItemResult) SetErrorMessage(v string)`

SetErrorMessage sets ErrorMessage field to given value.

### HasErrorMessage

`func (o *BatchItemResult) HasErrorMessage() bool`

HasErrorMessage returns a boolean if a field has been set.

### SetErrorMessageNil

`func (o *BatchItemResult) SetErrorMessageNil(b bool)`

 SetErrorMessageNil sets the value for ErrorMessage to be an explicit nil

### UnsetErrorMessage
`func (o *BatchItemResult) UnsetErrorMessage()`

UnsetErrorMessage ensures that no value is present for ErrorMessage, not even an explicit nil
### GetStatistics

`func (o *BatchItemResult) GetStatistics() map[string]interface{}`

GetStatistics returns the Statistics field if non-nil, zero value otherwise.

### GetStatisticsOk

`func (o *BatchItemResult) GetStatisticsOk() (*map[string]interface{}, bool)`

GetStatisticsOk returns a tuple with the Statistics field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatistics

`func (o *BatchItemResult) SetStatistics(v map[string]interface{})`

SetStatistics sets Statistics field to given value.

### HasStatistics

`func (o *BatchItemResult) HasStatistics() bool`

HasStatistics returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


