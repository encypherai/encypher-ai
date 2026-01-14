# MerkleProofItem

A single item in a Merkle proof path.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hash** | **str** | Hash value at this node | 
**position** | **str** | Position: &#39;left&#39; or &#39;right&#39; | 
**level** | **int** | Tree level (0 &#x3D; leaf) | 

## Example

```python
from encypher.models.merkle_proof_item import MerkleProofItem

# TODO update the JSON string below
json = "{}"
# create an instance of MerkleProofItem from a JSON string
merkle_proof_item_instance = MerkleProofItem.from_json(json)
# print the JSON string representation of the object
print(MerkleProofItem.to_json())

# convert the object into a dict
merkle_proof_item_dict = merkle_proof_item_instance.to_dict()
# create an instance of MerkleProofItem from a dict
merkle_proof_item_from_dict = MerkleProofItem.from_dict(merkle_proof_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


