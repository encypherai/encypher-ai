# VerifyEmbeddingResponse

Response from verifying an embedding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** | Whether embedding is valid | 
**ref_id** | **str** | Reference ID | 
**verified_at** | **datetime** |  | [optional] 
**content** | [**ContentInfo**](ContentInfo.md) |  | [optional] 
**document** | [**DocumentInfo**](DocumentInfo.md) |  | [optional] 
**merkle_proof** | [**MerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**c2pa** | [**C2PAInfo**](C2PAInfo.md) |  | [optional] 
**licensing** | [**LicensingInfo**](LicensingInfo.md) |  | [optional] 
**verification_url** | **str** |  | [optional] 
**error** | **str** |  | [optional] 

## Example

```python
from encypher.models.verify_embedding_response import VerifyEmbeddingResponse

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyEmbeddingResponse from a JSON string
verify_embedding_response_instance = VerifyEmbeddingResponse.from_json(json)
# print the JSON string representation of the object
print(VerifyEmbeddingResponse.to_json())

# convert the object into a dict
verify_embedding_response_dict = verify_embedding_response_instance.to_dict()
# create an instance of VerifyEmbeddingResponse from a dict
verify_embedding_response_from_dict = VerifyEmbeddingResponse.from_dict(verify_embedding_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


