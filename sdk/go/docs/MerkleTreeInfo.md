# MerkleTreeInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RootHash** | **string** | Merkle tree root hash | 
**TotalLeaves** | **int32** | Number of leaf nodes | 
**TreeDepth** | **int32** | Height of the tree | 

## Methods

### NewMerkleTreeInfo

`func NewMerkleTreeInfo(rootHash string, totalLeaves int32, treeDepth int32, ) *MerkleTreeInfo`

NewMerkleTreeInfo instantiates a new MerkleTreeInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMerkleTreeInfoWithDefaults

`func NewMerkleTreeInfoWithDefaults() *MerkleTreeInfo`

NewMerkleTreeInfoWithDefaults instantiates a new MerkleTreeInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRootHash

`func (o *MerkleTreeInfo) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *MerkleTreeInfo) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *MerkleTreeInfo) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetTotalLeaves

`func (o *MerkleTreeInfo) GetTotalLeaves() int32`

GetTotalLeaves returns the TotalLeaves field if non-nil, zero value otherwise.

### GetTotalLeavesOk

`func (o *MerkleTreeInfo) GetTotalLeavesOk() (*int32, bool)`

GetTotalLeavesOk returns a tuple with the TotalLeaves field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalLeaves

`func (o *MerkleTreeInfo) SetTotalLeaves(v int32)`

SetTotalLeaves sets TotalLeaves field to given value.


### GetTreeDepth

`func (o *MerkleTreeInfo) GetTreeDepth() int32`

GetTreeDepth returns the TreeDepth field if non-nil, zero value otherwise.

### GetTreeDepthOk

`func (o *MerkleTreeInfo) GetTreeDepthOk() (*int32, bool)`

GetTreeDepthOk returns a tuple with the TreeDepth field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTreeDepth

`func (o *MerkleTreeInfo) SetTreeDepth(v int32)`

SetTreeDepth sets TreeDepth field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


