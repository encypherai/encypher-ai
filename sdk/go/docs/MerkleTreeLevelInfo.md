# MerkleTreeLevelInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RootHash** | **string** | Root hash for the integrity proof | 
**TotalLeaves** | **int32** | Number of leaf nodes | 
**TreeDepth** | **int32** | Height of the tree | 
**Indexed** | **bool** | Whether the Merkle tree was indexed for attribution workflows | 

## Methods

### NewMerkleTreeLevelInfo

`func NewMerkleTreeLevelInfo(rootHash string, totalLeaves int32, treeDepth int32, indexed bool, ) *MerkleTreeLevelInfo`

NewMerkleTreeLevelInfo instantiates a new MerkleTreeLevelInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMerkleTreeLevelInfoWithDefaults

`func NewMerkleTreeLevelInfoWithDefaults() *MerkleTreeLevelInfo`

NewMerkleTreeLevelInfoWithDefaults instantiates a new MerkleTreeLevelInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRootHash

`func (o *MerkleTreeLevelInfo) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *MerkleTreeLevelInfo) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *MerkleTreeLevelInfo) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetTotalLeaves

`func (o *MerkleTreeLevelInfo) GetTotalLeaves() int32`

GetTotalLeaves returns the TotalLeaves field if non-nil, zero value otherwise.

### GetTotalLeavesOk

`func (o *MerkleTreeLevelInfo) GetTotalLeavesOk() (*int32, bool)`

GetTotalLeavesOk returns a tuple with the TotalLeaves field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalLeaves

`func (o *MerkleTreeLevelInfo) SetTotalLeaves(v int32)`

SetTotalLeaves sets TotalLeaves field to given value.


### GetTreeDepth

`func (o *MerkleTreeLevelInfo) GetTreeDepth() int32`

GetTreeDepth returns the TreeDepth field if non-nil, zero value otherwise.

### GetTreeDepthOk

`func (o *MerkleTreeLevelInfo) GetTreeDepthOk() (*int32, bool)`

GetTreeDepthOk returns a tuple with the TreeDepth field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTreeDepth

`func (o *MerkleTreeLevelInfo) SetTreeDepth(v int32)`

SetTreeDepth sets TreeDepth field to given value.


### GetIndexed

`func (o *MerkleTreeLevelInfo) GetIndexed() bool`

GetIndexed returns the Indexed field if non-nil, zero value otherwise.

### GetIndexedOk

`func (o *MerkleTreeLevelInfo) GetIndexedOk() (*bool, bool)`

GetIndexedOk returns a tuple with the Indexed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIndexed

`func (o *MerkleTreeLevelInfo) SetIndexed(v bool)`

SetIndexed sets Indexed field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


