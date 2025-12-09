# BatchVerifyResult

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RefId** | **string** | Reference ID | 
**Valid** | **bool** | Whether embedding is valid | 
**DocumentId** | Pointer to **NullableString** |  | [optional] 
**TextPreview** | Pointer to **NullableString** |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewBatchVerifyResult

`func NewBatchVerifyResult(refId string, valid bool, ) *BatchVerifyResult`

NewBatchVerifyResult instantiates a new BatchVerifyResult object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchVerifyResultWithDefaults

`func NewBatchVerifyResultWithDefaults() *BatchVerifyResult`

NewBatchVerifyResultWithDefaults instantiates a new BatchVerifyResult object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRefId

`func (o *BatchVerifyResult) GetRefId() string`

GetRefId returns the RefId field if non-nil, zero value otherwise.

### GetRefIdOk

`func (o *BatchVerifyResult) GetRefIdOk() (*string, bool)`

GetRefIdOk returns a tuple with the RefId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRefId

`func (o *BatchVerifyResult) SetRefId(v string)`

SetRefId sets RefId field to given value.


### GetValid

`func (o *BatchVerifyResult) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *BatchVerifyResult) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *BatchVerifyResult) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetDocumentId

`func (o *BatchVerifyResult) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *BatchVerifyResult) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *BatchVerifyResult) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.

### HasDocumentId

`func (o *BatchVerifyResult) HasDocumentId() bool`

HasDocumentId returns a boolean if a field has been set.

### SetDocumentIdNil

`func (o *BatchVerifyResult) SetDocumentIdNil(b bool)`

 SetDocumentIdNil sets the value for DocumentId to be an explicit nil

### UnsetDocumentId
`func (o *BatchVerifyResult) UnsetDocumentId()`

UnsetDocumentId ensures that no value is present for DocumentId, not even an explicit nil
### GetTextPreview

`func (o *BatchVerifyResult) GetTextPreview() string`

GetTextPreview returns the TextPreview field if non-nil, zero value otherwise.

### GetTextPreviewOk

`func (o *BatchVerifyResult) GetTextPreviewOk() (*string, bool)`

GetTextPreviewOk returns a tuple with the TextPreview field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextPreview

`func (o *BatchVerifyResult) SetTextPreview(v string)`

SetTextPreview sets TextPreview field to given value.

### HasTextPreview

`func (o *BatchVerifyResult) HasTextPreview() bool`

HasTextPreview returns a boolean if a field has been set.

### SetTextPreviewNil

`func (o *BatchVerifyResult) SetTextPreviewNil(b bool)`

 SetTextPreviewNil sets the value for TextPreview to be an explicit nil

### UnsetTextPreview
`func (o *BatchVerifyResult) UnsetTextPreview()`

UnsetTextPreview ensures that no value is present for TextPreview, not even an explicit nil
### GetError

`func (o *BatchVerifyResult) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *BatchVerifyResult) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *BatchVerifyResult) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *BatchVerifyResult) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *BatchVerifyResult) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *BatchVerifyResult) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


