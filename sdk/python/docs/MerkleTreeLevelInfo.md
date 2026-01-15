# MerkleTreeLevelInfo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_hash** | **str** | Root hash for the integrity proof | 
**total_leaves** | **int** | Number of leaf nodes | 
**tree_depth** | **int** | Height of the tree | 
**indexed** | **bool** | Whether the Merkle tree was indexed for attribution workflows | 

## Example

```python
from encypher.models.merkle_tree_level_info import MerkleTreeLevelInfo

# TODO update the JSON string below
json = "{}"
# create an instance of MerkleTreeLevelInfo from a JSON string
merkle_tree_level_info_instance = MerkleTreeLevelInfo.from_json(json)
# print the JSON string representation of the object
print(MerkleTreeLevelInfo.to_json())

# convert the object into a dict
merkle_tree_level_info_dict = merkle_tree_level_info_instance.to_dict()
# create an instance of MerkleTreeLevelInfo from a dict
merkle_tree_level_info_from_dict = MerkleTreeLevelInfo.from_dict(merkle_tree_level_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


