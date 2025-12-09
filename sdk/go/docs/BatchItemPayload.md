# BatchItemPayload

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Unique document identifier | 
**Text** | **string** | Raw document text to process | 
**Title** | Pointer to **NullableString** |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewBatchItemPayload

`func NewBatchItemPayload(documentId string, text string, ) *BatchItemPayload`

NewBatchItemPayload instantiates a new BatchItemPayload object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchItemPayloadWithDefaults

`func NewBatchItemPayloadWithDefaults() *BatchItemPayload`

NewBatchItemPayloadWithDefaults instantiates a new BatchItemPayload object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *BatchItemPayload) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *BatchItemPayload) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *BatchItemPayload) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetText

`func (o *BatchItemPayload) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *BatchItemPayload) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *BatchItemPayload) SetText(v string)`

SetText sets Text field to given value.


### GetTitle

`func (o *BatchItemPayload) GetTitle() string`

GetTitle returns the Title field if non-nil, zero value otherwise.

### GetTitleOk

`func (o *BatchItemPayload) GetTitleOk() (*string, bool)`

GetTitleOk returns a tuple with the Title field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTitle

`func (o *BatchItemPayload) SetTitle(v string)`

SetTitle sets Title field to given value.

### HasTitle

`func (o *BatchItemPayload) HasTitle() bool`

HasTitle returns a boolean if a field has been set.

### SetTitleNil

`func (o *BatchItemPayload) SetTitleNil(b bool)`

 SetTitleNil sets the value for Title to be an explicit nil

### UnsetTitle
`func (o *BatchItemPayload) UnsetTitle()`

UnsetTitle ensures that no value is present for Title, not even an explicit nil
### GetMetadata

`func (o *BatchItemPayload) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *BatchItemPayload) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *BatchItemPayload) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *BatchItemPayload) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *BatchItemPayload) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *BatchItemPayload) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


