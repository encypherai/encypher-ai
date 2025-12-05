# MerkleRootResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RootId** | **string** | Unique identifier for the Merkle root | 
**DocumentId** | **string** | Document identifier | 
**RootHash** | **string** | SHA-256 hash of the Merkle tree root | 
**TreeDepth** | **int32** | Height of the Merkle tree | 
**TotalLeaves** | **int32** | Number of leaf nodes in the tree | 
**SegmentationLevel** | **string** | Segmentation level (word/sentence/paragraph/section) | 
**CreatedAt** | **time.Time** | Timestamp when the root was created | 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewMerkleRootResponse

`func NewMerkleRootResponse(rootId string, documentId string, rootHash string, treeDepth int32, totalLeaves int32, segmentationLevel string, createdAt time.Time, ) *MerkleRootResponse`

NewMerkleRootResponse instantiates a new MerkleRootResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMerkleRootResponseWithDefaults

`func NewMerkleRootResponseWithDefaults() *MerkleRootResponse`

NewMerkleRootResponseWithDefaults instantiates a new MerkleRootResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRootId

`func (o *MerkleRootResponse) GetRootId() string`

GetRootId returns the RootId field if non-nil, zero value otherwise.

### GetRootIdOk

`func (o *MerkleRootResponse) GetRootIdOk() (*string, bool)`

GetRootIdOk returns a tuple with the RootId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootId

`func (o *MerkleRootResponse) SetRootId(v string)`

SetRootId sets RootId field to given value.


### GetDocumentId

`func (o *MerkleRootResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *MerkleRootResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *MerkleRootResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetRootHash

`func (o *MerkleRootResponse) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *MerkleRootResponse) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *MerkleRootResponse) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetTreeDepth

`func (o *MerkleRootResponse) GetTreeDepth() int32`

GetTreeDepth returns the TreeDepth field if non-nil, zero value otherwise.

### GetTreeDepthOk

`func (o *MerkleRootResponse) GetTreeDepthOk() (*int32, bool)`

GetTreeDepthOk returns a tuple with the TreeDepth field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTreeDepth

`func (o *MerkleRootResponse) SetTreeDepth(v int32)`

SetTreeDepth sets TreeDepth field to given value.


### GetTotalLeaves

`func (o *MerkleRootResponse) GetTotalLeaves() int32`

GetTotalLeaves returns the TotalLeaves field if non-nil, zero value otherwise.

### GetTotalLeavesOk

`func (o *MerkleRootResponse) GetTotalLeavesOk() (*int32, bool)`

GetTotalLeavesOk returns a tuple with the TotalLeaves field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalLeaves

`func (o *MerkleRootResponse) SetTotalLeaves(v int32)`

SetTotalLeaves sets TotalLeaves field to given value.


### GetSegmentationLevel

`func (o *MerkleRootResponse) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *MerkleRootResponse) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *MerkleRootResponse) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.


### GetCreatedAt

`func (o *MerkleRootResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *MerkleRootResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *MerkleRootResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetMetadata

`func (o *MerkleRootResponse) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *MerkleRootResponse) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *MerkleRootResponse) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *MerkleRootResponse) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *MerkleRootResponse) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *MerkleRootResponse) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


