# MerkleProofInfo

Merkle proof information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_hash** | **str** | Merkle tree root hash | 
**verified** | **bool** | Whether proof is valid | 
**proof_url** | **str** |  | [optional] 

## Example

```python
from encypher.models.merkle_proof_info import MerkleProofInfo

# TODO update the JSON string below
json = "{}"
# create an instance of MerkleProofInfo from a JSON string
merkle_proof_info_instance = MerkleProofInfo.from_json(json)
# print the JSON string representation of the object
print(MerkleProofInfo.to_json())

# convert the object into a dict
merkle_proof_info_dict = merkle_proof_info_instance.to_dict()
# create an instance of MerkleProofInfo from a dict
merkle_proof_info_from_dict = MerkleProofInfo.from_dict(merkle_proof_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


