# VerificationServiceMerkleProofInfo

Merkle tree proof information (paid feature).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**root_hash** | **str** |  | [optional] 
**leaf_hash** | **str** |  | [optional] 
**leaf_index** | **int** |  | [optional] 
**proof_path** | **List[str]** |  | [optional] 
**verified** | **bool** |  | [optional] [default to False]

## Example

```python
from encypher.models.verification_service_merkle_proof_info import VerificationServiceMerkleProofInfo

# TODO update the JSON string below
json = "{}"
# create an instance of VerificationServiceMerkleProofInfo from a JSON string
verification_service_merkle_proof_info_instance = VerificationServiceMerkleProofInfo.from_json(json)
# print the JSON string representation of the object
print(VerificationServiceMerkleProofInfo.to_json())

# convert the object into a dict
verification_service_merkle_proof_info_dict = verification_service_merkle_proof_info_instance.to_dict()
# create an instance of VerificationServiceMerkleProofInfo from a dict
verification_service_merkle_proof_info_from_dict = VerificationServiceMerkleProofInfo.from_dict(verification_service_merkle_proof_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


