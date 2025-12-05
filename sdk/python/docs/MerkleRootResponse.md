# MerkleRootResponse

Response schema for a single Merkle root.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_id** | **str** | Unique identifier for the Merkle root | 
**document_id** | **str** | Document identifier | 
**root_hash** | **str** | SHA-256 hash of the Merkle tree root | 
**tree_depth** | **int** | Height of the Merkle tree | 
**total_leaves** | **int** | Number of leaf nodes in the tree | 
**segmentation_level** | **str** | Segmentation level (word/sentence/paragraph/section) | 
**created_at** | **datetime** | Timestamp when the root was created | 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.merkle_root_response import MerkleRootResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MerkleRootResponse from a JSON string
merkle_root_response_instance = MerkleRootResponse.from_json(json)
# print the JSON string representation of the object
print(MerkleRootResponse.to_json())

# convert the object into a dict
merkle_root_response_dict = merkle_root_response_instance.to_dict()
# create an instance of MerkleRootResponse from a dict
merkle_root_response_from_dict = MerkleRootResponse.from_dict(merkle_root_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


