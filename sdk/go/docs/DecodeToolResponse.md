# DecodeToolResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**VerificationStatus** | Pointer to **string** |  | [optional] [default to "Not Attempted"]
**Error** | Pointer to **NullableString** |  | [optional] 
**RawHiddenData** | Pointer to [**NullableAppRoutersToolsVerifyVerdict**](AppRoutersToolsVerifyVerdict.md) |  | [optional] 
**EmbeddingsFound** | Pointer to **int32** | Number of embeddings found in the text | [optional] [default to 0]
**AllEmbeddings** | Pointer to [**[]EmbeddingResult**](EmbeddingResult.md) |  | [optional] 

## Methods

### NewDecodeToolResponse

`func NewDecodeToolResponse() *DecodeToolResponse`

NewDecodeToolResponse instantiates a new DecodeToolResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDecodeToolResponseWithDefaults

`func NewDecodeToolResponseWithDefaults() *DecodeToolResponse`

NewDecodeToolResponseWithDefaults instantiates a new DecodeToolResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMetadata

`func (o *DecodeToolResponse) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *DecodeToolResponse) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *DecodeToolResponse) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *DecodeToolResponse) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *DecodeToolResponse) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *DecodeToolResponse) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetVerificationStatus

`func (o *DecodeToolResponse) GetVerificationStatus() string`

GetVerificationStatus returns the VerificationStatus field if non-nil, zero value otherwise.

### GetVerificationStatusOk

`func (o *DecodeToolResponse) GetVerificationStatusOk() (*string, bool)`

GetVerificationStatusOk returns a tuple with the VerificationStatus field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationStatus

`func (o *DecodeToolResponse) SetVerificationStatus(v string)`

SetVerificationStatus sets VerificationStatus field to given value.

### HasVerificationStatus

`func (o *DecodeToolResponse) HasVerificationStatus() bool`

HasVerificationStatus returns a boolean if a field has been set.

### GetError

`func (o *DecodeToolResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *DecodeToolResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *DecodeToolResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *DecodeToolResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *DecodeToolResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *DecodeToolResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil
### GetRawHiddenData

`func (o *DecodeToolResponse) GetRawHiddenData() AppRoutersToolsVerifyVerdict`

GetRawHiddenData returns the RawHiddenData field if non-nil, zero value otherwise.

### GetRawHiddenDataOk

`func (o *DecodeToolResponse) GetRawHiddenDataOk() (*AppRoutersToolsVerifyVerdict, bool)`

GetRawHiddenDataOk returns a tuple with the RawHiddenData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRawHiddenData

`func (o *DecodeToolResponse) SetRawHiddenData(v AppRoutersToolsVerifyVerdict)`

SetRawHiddenData sets RawHiddenData field to given value.

### HasRawHiddenData

`func (o *DecodeToolResponse) HasRawHiddenData() bool`

HasRawHiddenData returns a boolean if a field has been set.

### SetRawHiddenDataNil

`func (o *DecodeToolResponse) SetRawHiddenDataNil(b bool)`

 SetRawHiddenDataNil sets the value for RawHiddenData to be an explicit nil

### UnsetRawHiddenData
`func (o *DecodeToolResponse) UnsetRawHiddenData()`

UnsetRawHiddenData ensures that no value is present for RawHiddenData, not even an explicit nil
### GetEmbeddingsFound

`func (o *DecodeToolResponse) GetEmbeddingsFound() int32`

GetEmbeddingsFound returns the EmbeddingsFound field if non-nil, zero value otherwise.

### GetEmbeddingsFoundOk

`func (o *DecodeToolResponse) GetEmbeddingsFoundOk() (*int32, bool)`

GetEmbeddingsFoundOk returns a tuple with the EmbeddingsFound field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingsFound

`func (o *DecodeToolResponse) SetEmbeddingsFound(v int32)`

SetEmbeddingsFound sets EmbeddingsFound field to given value.

### HasEmbeddingsFound

`func (o *DecodeToolResponse) HasEmbeddingsFound() bool`

HasEmbeddingsFound returns a boolean if a field has been set.

### GetAllEmbeddings

`func (o *DecodeToolResponse) GetAllEmbeddings() []EmbeddingResult`

GetAllEmbeddings returns the AllEmbeddings field if non-nil, zero value otherwise.

### GetAllEmbeddingsOk

`func (o *DecodeToolResponse) GetAllEmbeddingsOk() (*[]EmbeddingResult, bool)`

GetAllEmbeddingsOk returns a tuple with the AllEmbeddings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllEmbeddings

`func (o *DecodeToolResponse) SetAllEmbeddings(v []EmbeddingResult)`

SetAllEmbeddings sets AllEmbeddings field to given value.

### HasAllEmbeddings

`func (o *DecodeToolResponse) HasAllEmbeddings() bool`

HasAllEmbeddings returns a boolean if a field has been set.

### SetAllEmbeddingsNil

`func (o *DecodeToolResponse) SetAllEmbeddingsNil(b bool)`

 SetAllEmbeddingsNil sets the value for AllEmbeddings to be an explicit nil

### UnsetAllEmbeddings
`func (o *DecodeToolResponse) UnsetAllEmbeddings()`

UnsetAllEmbeddings ensures that no value is present for AllEmbeddings, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


