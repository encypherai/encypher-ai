# EncodeWithEmbeddingsResponse

Response from encoding document with embeddings.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether encoding succeeded | [optional] [default to True]
**document_id** | **str** | Document identifier | 
**merkle_tree** | [**MerkleTreeInfo**](MerkleTreeInfo.md) |  | [optional] 
**merkle_trees** | [**Dict[str, MerkleTreeLevelInfo]**](MerkleTreeLevelInfo.md) |  | [optional] 
**embeddings** | [**List[EmbeddingInfo]**](EmbeddingInfo.md) | List of generated embeddings | 
**embedded_content** | **str** |  | [optional] 
**statistics** | **Dict[str, object]** | Processing statistics | 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.encode_with_embeddings_response import EncodeWithEmbeddingsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EncodeWithEmbeddingsResponse from a JSON string
encode_with_embeddings_response_instance = EncodeWithEmbeddingsResponse.from_json(json)
# print the JSON string representation of the object
print(EncodeWithEmbeddingsResponse.to_json())

# convert the object into a dict
encode_with_embeddings_response_dict = encode_with_embeddings_response_instance.to_dict()
# create an instance of EncodeWithEmbeddingsResponse from a dict
encode_with_embeddings_response_from_dict = EncodeWithEmbeddingsResponse.from_dict(encode_with_embeddings_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


