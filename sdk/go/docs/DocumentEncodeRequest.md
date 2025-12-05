# DocumentEncodeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Unique identifier for the document | 
**Text** | **string** | Document text content to encode | 
**SegmentationLevels** | Pointer to **[]string** | Segmentation levels to encode (word/sentence/paragraph/section) | [optional] [default to [sentence]]
**IncludeWords** | Pointer to **bool** | Whether to include word-level segmentation | [optional] [default to false]
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewDocumentEncodeRequest

`func NewDocumentEncodeRequest(documentId string, text string, ) *DocumentEncodeRequest`

NewDocumentEncodeRequest instantiates a new DocumentEncodeRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentEncodeRequestWithDefaults

`func NewDocumentEncodeRequestWithDefaults() *DocumentEncodeRequest`

NewDocumentEncodeRequestWithDefaults instantiates a new DocumentEncodeRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *DocumentEncodeRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *DocumentEncodeRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *DocumentEncodeRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetText

`func (o *DocumentEncodeRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *DocumentEncodeRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *DocumentEncodeRequest) SetText(v string)`

SetText sets Text field to given value.


### GetSegmentationLevels

`func (o *DocumentEncodeRequest) GetSegmentationLevels() []string`

GetSegmentationLevels returns the SegmentationLevels field if non-nil, zero value otherwise.

### GetSegmentationLevelsOk

`func (o *DocumentEncodeRequest) GetSegmentationLevelsOk() (*[]string, bool)`

GetSegmentationLevelsOk returns a tuple with the SegmentationLevels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevels

`func (o *DocumentEncodeRequest) SetSegmentationLevels(v []string)`

SetSegmentationLevels sets SegmentationLevels field to given value.

### HasSegmentationLevels

`func (o *DocumentEncodeRequest) HasSegmentationLevels() bool`

HasSegmentationLevels returns a boolean if a field has been set.

### GetIncludeWords

`func (o *DocumentEncodeRequest) GetIncludeWords() bool`

GetIncludeWords returns the IncludeWords field if non-nil, zero value otherwise.

### GetIncludeWordsOk

`func (o *DocumentEncodeRequest) GetIncludeWordsOk() (*bool, bool)`

GetIncludeWordsOk returns a tuple with the IncludeWords field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeWords

`func (o *DocumentEncodeRequest) SetIncludeWords(v bool)`

SetIncludeWords sets IncludeWords field to given value.

### HasIncludeWords

`func (o *DocumentEncodeRequest) HasIncludeWords() bool`

HasIncludeWords returns a boolean if a field has been set.

### GetMetadata

`func (o *DocumentEncodeRequest) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *DocumentEncodeRequest) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *DocumentEncodeRequest) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *DocumentEncodeRequest) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *DocumentEncodeRequest) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *DocumentEncodeRequest) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


