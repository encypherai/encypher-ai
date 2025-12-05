# EncodeWithEmbeddingsResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** | Whether encoding succeeded | [optional] [default to true]
**DocumentId** | **string** | Document identifier | 
**MerkleTree** | Pointer to [**NullableMerkleTreeInfo**](MerkleTreeInfo.md) |  | [optional] 
**Embeddings** | [**[]EmbeddingInfo**](EmbeddingInfo.md) | List of generated embeddings | 
**EmbeddedContent** | Pointer to **NullableString** |  | [optional] 
**Statistics** | **map[string]interface{}** | Processing statistics | 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewEncodeWithEmbeddingsResponse

`func NewEncodeWithEmbeddingsResponse(documentId string, embeddings []EmbeddingInfo, statistics map[string]interface{}, ) *EncodeWithEmbeddingsResponse`

NewEncodeWithEmbeddingsResponse instantiates a new EncodeWithEmbeddingsResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEncodeWithEmbeddingsResponseWithDefaults

`func NewEncodeWithEmbeddingsResponseWithDefaults() *EncodeWithEmbeddingsResponse`

NewEncodeWithEmbeddingsResponseWithDefaults instantiates a new EncodeWithEmbeddingsResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *EncodeWithEmbeddingsResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *EncodeWithEmbeddingsResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *EncodeWithEmbeddingsResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *EncodeWithEmbeddingsResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetDocumentId

`func (o *EncodeWithEmbeddingsResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *EncodeWithEmbeddingsResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *EncodeWithEmbeddingsResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetMerkleTree

`func (o *EncodeWithEmbeddingsResponse) GetMerkleTree() MerkleTreeInfo`

GetMerkleTree returns the MerkleTree field if non-nil, zero value otherwise.

### GetMerkleTreeOk

`func (o *EncodeWithEmbeddingsResponse) GetMerkleTreeOk() (*MerkleTreeInfo, bool)`

GetMerkleTreeOk returns a tuple with the MerkleTree field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleTree

`func (o *EncodeWithEmbeddingsResponse) SetMerkleTree(v MerkleTreeInfo)`

SetMerkleTree sets MerkleTree field to given value.

### HasMerkleTree

`func (o *EncodeWithEmbeddingsResponse) HasMerkleTree() bool`

HasMerkleTree returns a boolean if a field has been set.

### SetMerkleTreeNil

`func (o *EncodeWithEmbeddingsResponse) SetMerkleTreeNil(b bool)`

 SetMerkleTreeNil sets the value for MerkleTree to be an explicit nil

### UnsetMerkleTree
`func (o *EncodeWithEmbeddingsResponse) UnsetMerkleTree()`

UnsetMerkleTree ensures that no value is present for MerkleTree, not even an explicit nil
### GetEmbeddings

`func (o *EncodeWithEmbeddingsResponse) GetEmbeddings() []EmbeddingInfo`

GetEmbeddings returns the Embeddings field if non-nil, zero value otherwise.

### GetEmbeddingsOk

`func (o *EncodeWithEmbeddingsResponse) GetEmbeddingsOk() (*[]EmbeddingInfo, bool)`

GetEmbeddingsOk returns a tuple with the Embeddings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddings

`func (o *EncodeWithEmbeddingsResponse) SetEmbeddings(v []EmbeddingInfo)`

SetEmbeddings sets Embeddings field to given value.


### GetEmbeddedContent

`func (o *EncodeWithEmbeddingsResponse) GetEmbeddedContent() string`

GetEmbeddedContent returns the EmbeddedContent field if non-nil, zero value otherwise.

### GetEmbeddedContentOk

`func (o *EncodeWithEmbeddingsResponse) GetEmbeddedContentOk() (*string, bool)`

GetEmbeddedContentOk returns a tuple with the EmbeddedContent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddedContent

`func (o *EncodeWithEmbeddingsResponse) SetEmbeddedContent(v string)`

SetEmbeddedContent sets EmbeddedContent field to given value.

### HasEmbeddedContent

`func (o *EncodeWithEmbeddingsResponse) HasEmbeddedContent() bool`

HasEmbeddedContent returns a boolean if a field has been set.

### SetEmbeddedContentNil

`func (o *EncodeWithEmbeddingsResponse) SetEmbeddedContentNil(b bool)`

 SetEmbeddedContentNil sets the value for EmbeddedContent to be an explicit nil

### UnsetEmbeddedContent
`func (o *EncodeWithEmbeddingsResponse) UnsetEmbeddedContent()`

UnsetEmbeddedContent ensures that no value is present for EmbeddedContent, not even an explicit nil
### GetStatistics

`func (o *EncodeWithEmbeddingsResponse) GetStatistics() map[string]interface{}`

GetStatistics returns the Statistics field if non-nil, zero value otherwise.

### GetStatisticsOk

`func (o *EncodeWithEmbeddingsResponse) GetStatisticsOk() (*map[string]interface{}, bool)`

GetStatisticsOk returns a tuple with the Statistics field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatistics

`func (o *EncodeWithEmbeddingsResponse) SetStatistics(v map[string]interface{})`

SetStatistics sets Statistics field to given value.


### GetMetadata

`func (o *EncodeWithEmbeddingsResponse) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *EncodeWithEmbeddingsResponse) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *EncodeWithEmbeddingsResponse) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *EncodeWithEmbeddingsResponse) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *EncodeWithEmbeddingsResponse) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *EncodeWithEmbeddingsResponse) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


