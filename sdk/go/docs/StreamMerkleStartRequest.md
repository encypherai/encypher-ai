# StreamMerkleStartRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Unique document identifier | 
**SegmentationLevel** | Pointer to **string** | Segmentation level: sentence, paragraph, section | [optional] [default to "sentence"]
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**BufferSize** | Pointer to **int32** | Maximum number of segments to buffer before forcing a flush | [optional] [default to 100]
**AutoFinalizeTimeoutSeconds** | Pointer to **int32** | Timeout in seconds after which session auto-finalizes if idle | [optional] [default to 300]

## Methods

### NewStreamMerkleStartRequest

`func NewStreamMerkleStartRequest(documentId string, ) *StreamMerkleStartRequest`

NewStreamMerkleStartRequest instantiates a new StreamMerkleStartRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleStartRequestWithDefaults

`func NewStreamMerkleStartRequestWithDefaults() *StreamMerkleStartRequest`

NewStreamMerkleStartRequestWithDefaults instantiates a new StreamMerkleStartRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *StreamMerkleStartRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *StreamMerkleStartRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *StreamMerkleStartRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetSegmentationLevel

`func (o *StreamMerkleStartRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *StreamMerkleStartRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *StreamMerkleStartRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *StreamMerkleStartRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetMetadata

`func (o *StreamMerkleStartRequest) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *StreamMerkleStartRequest) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *StreamMerkleStartRequest) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *StreamMerkleStartRequest) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *StreamMerkleStartRequest) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *StreamMerkleStartRequest) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetBufferSize

`func (o *StreamMerkleStartRequest) GetBufferSize() int32`

GetBufferSize returns the BufferSize field if non-nil, zero value otherwise.

### GetBufferSizeOk

`func (o *StreamMerkleStartRequest) GetBufferSizeOk() (*int32, bool)`

GetBufferSizeOk returns a tuple with the BufferSize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBufferSize

`func (o *StreamMerkleStartRequest) SetBufferSize(v int32)`

SetBufferSize sets BufferSize field to given value.

### HasBufferSize

`func (o *StreamMerkleStartRequest) HasBufferSize() bool`

HasBufferSize returns a boolean if a field has been set.

### GetAutoFinalizeTimeoutSeconds

`func (o *StreamMerkleStartRequest) GetAutoFinalizeTimeoutSeconds() int32`

GetAutoFinalizeTimeoutSeconds returns the AutoFinalizeTimeoutSeconds field if non-nil, zero value otherwise.

### GetAutoFinalizeTimeoutSecondsOk

`func (o *StreamMerkleStartRequest) GetAutoFinalizeTimeoutSecondsOk() (*int32, bool)`

GetAutoFinalizeTimeoutSecondsOk returns a tuple with the AutoFinalizeTimeoutSeconds field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAutoFinalizeTimeoutSeconds

`func (o *StreamMerkleStartRequest) SetAutoFinalizeTimeoutSeconds(v int32)`

SetAutoFinalizeTimeoutSeconds sets AutoFinalizeTimeoutSeconds field to given value.

### HasAutoFinalizeTimeoutSeconds

`func (o *StreamMerkleStartRequest) HasAutoFinalizeTimeoutSeconds() bool`

HasAutoFinalizeTimeoutSeconds returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


