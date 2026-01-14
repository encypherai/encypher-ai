# MerkleTreeInfo

Merkle tree information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_hash** | **str** | Root hash for the integrity proof | 
**total_leaves** | **int** | Number of leaf nodes | 
**tree_depth** | **int** | Height of the tree | 

## Example

```python
from encypher.models.merkle_tree_info import MerkleTreeInfo

# TODO update the JSON string below
json = "{}"
# create an instance of MerkleTreeInfo from a JSON string
merkle_tree_info_instance = MerkleTreeInfo.from_json(json)
# print the JSON string representation of the object
print(MerkleTreeInfo.to_json())

# convert the object into a dict
merkle_tree_info_dict = merkle_tree_info_instance.to_dict()
# create an instance of MerkleTreeInfo from a dict
merkle_tree_info_from_dict = MerkleTreeInfo.from_dict(merkle_tree_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


