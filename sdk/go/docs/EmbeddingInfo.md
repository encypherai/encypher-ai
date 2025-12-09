# EmbeddingInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**LeafIndex** | **int32** | Position in document (0-indexed) | 
**Text** | Pointer to **NullableString** |  | [optional] 
**RefId** | Pointer to **NullableString** |  | [optional] 
**Signature** | Pointer to **NullableString** |  | [optional] 
**Embedding** | Pointer to **NullableString** |  | [optional] 
**VerificationUrl** | Pointer to **NullableString** |  | [optional] 
**LeafHash** | **string** | SHA-256 hash of text segment | 

## Methods

### NewEmbeddingInfo

`func NewEmbeddingInfo(leafIndex int32, leafHash string, ) *EmbeddingInfo`

NewEmbeddingInfo instantiates a new EmbeddingInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEmbeddingInfoWithDefaults

`func NewEmbeddingInfoWithDefaults() *EmbeddingInfo`

NewEmbeddingInfoWithDefaults instantiates a new EmbeddingInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetLeafIndex

`func (o *EmbeddingInfo) GetLeafIndex() int32`

GetLeafIndex returns the LeafIndex field if non-nil, zero value otherwise.

### GetLeafIndexOk

`func (o *EmbeddingInfo) GetLeafIndexOk() (*int32, bool)`

GetLeafIndexOk returns a tuple with the LeafIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafIndex

`func (o *EmbeddingInfo) SetLeafIndex(v int32)`

SetLeafIndex sets LeafIndex field to given value.


### GetText

`func (o *EmbeddingInfo) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *EmbeddingInfo) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *EmbeddingInfo) SetText(v string)`

SetText sets Text field to given value.

### HasText

`func (o *EmbeddingInfo) HasText() bool`

HasText returns a boolean if a field has been set.

### SetTextNil

`func (o *EmbeddingInfo) SetTextNil(b bool)`

 SetTextNil sets the value for Text to be an explicit nil

### UnsetText
`func (o *EmbeddingInfo) UnsetText()`

UnsetText ensures that no value is present for Text, not even an explicit nil
### GetRefId

`func (o *EmbeddingInfo) GetRefId() string`

GetRefId returns the RefId field if non-nil, zero value otherwise.

### GetRefIdOk

`func (o *EmbeddingInfo) GetRefIdOk() (*string, bool)`

GetRefIdOk returns a tuple with the RefId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRefId

`func (o *EmbeddingInfo) SetRefId(v string)`

SetRefId sets RefId field to given value.

### HasRefId

`func (o *EmbeddingInfo) HasRefId() bool`

HasRefId returns a boolean if a field has been set.

### SetRefIdNil

`func (o *EmbeddingInfo) SetRefIdNil(b bool)`

 SetRefIdNil sets the value for RefId to be an explicit nil

### UnsetRefId
`func (o *EmbeddingInfo) UnsetRefId()`

UnsetRefId ensures that no value is present for RefId, not even an explicit nil
### GetSignature

`func (o *EmbeddingInfo) GetSignature() string`

GetSignature returns the Signature field if non-nil, zero value otherwise.

### GetSignatureOk

`func (o *EmbeddingInfo) GetSignatureOk() (*string, bool)`

GetSignatureOk returns a tuple with the Signature field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignature

`func (o *EmbeddingInfo) SetSignature(v string)`

SetSignature sets Signature field to given value.

### HasSignature

`func (o *EmbeddingInfo) HasSignature() bool`

HasSignature returns a boolean if a field has been set.

### SetSignatureNil

`func (o *EmbeddingInfo) SetSignatureNil(b bool)`

 SetSignatureNil sets the value for Signature to be an explicit nil

### UnsetSignature
`func (o *EmbeddingInfo) UnsetSignature()`

UnsetSignature ensures that no value is present for Signature, not even an explicit nil
### GetEmbedding

`func (o *EmbeddingInfo) GetEmbedding() string`

GetEmbedding returns the Embedding field if non-nil, zero value otherwise.

### GetEmbeddingOk

`func (o *EmbeddingInfo) GetEmbeddingOk() (*string, bool)`

GetEmbeddingOk returns a tuple with the Embedding field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbedding

`func (o *EmbeddingInfo) SetEmbedding(v string)`

SetEmbedding sets Embedding field to given value.

### HasEmbedding

`func (o *EmbeddingInfo) HasEmbedding() bool`

HasEmbedding returns a boolean if a field has been set.

### SetEmbeddingNil

`func (o *EmbeddingInfo) SetEmbeddingNil(b bool)`

 SetEmbeddingNil sets the value for Embedding to be an explicit nil

### UnsetEmbedding
`func (o *EmbeddingInfo) UnsetEmbedding()`

UnsetEmbedding ensures that no value is present for Embedding, not even an explicit nil
### GetVerificationUrl

`func (o *EmbeddingInfo) GetVerificationUrl() string`

GetVerificationUrl returns the VerificationUrl field if non-nil, zero value otherwise.

### GetVerificationUrlOk

`func (o *EmbeddingInfo) GetVerificationUrlOk() (*string, bool)`

GetVerificationUrlOk returns a tuple with the VerificationUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationUrl

`func (o *EmbeddingInfo) SetVerificationUrl(v string)`

SetVerificationUrl sets VerificationUrl field to given value.

### HasVerificationUrl

`func (o *EmbeddingInfo) HasVerificationUrl() bool`

HasVerificationUrl returns a boolean if a field has been set.

### SetVerificationUrlNil

`func (o *EmbeddingInfo) SetVerificationUrlNil(b bool)`

 SetVerificationUrlNil sets the value for VerificationUrl to be an explicit nil

### UnsetVerificationUrl
`func (o *EmbeddingInfo) UnsetVerificationUrl()`

UnsetVerificationUrl ensures that no value is present for VerificationUrl, not even an explicit nil
### GetLeafHash

`func (o *EmbeddingInfo) GetLeafHash() string`

GetLeafHash returns the LeafHash field if non-nil, zero value otherwise.

### GetLeafHashOk

`func (o *EmbeddingInfo) GetLeafHashOk() (*string, bool)`

GetLeafHashOk returns a tuple with the LeafHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafHash

`func (o *EmbeddingInfo) SetLeafHash(v string)`

SetLeafHash sets LeafHash field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


