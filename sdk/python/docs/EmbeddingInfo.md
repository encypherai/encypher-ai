# EmbeddingInfo

Information about a single embedding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**leaf_index** | **int** | Position in document (0-indexed) | 
**text** | **str** |  | [optional] 
**ref_id** | **str** |  | [optional] 
**signature** | **str** |  | [optional] 
**embedding** | **str** |  | [optional] 
**verification_url** | **str** |  | [optional] 
**leaf_hash** | **str** | Cryptographic hash of the signed text segment | 

## Example

```python
from encypher.models.embedding_info import EmbeddingInfo

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingInfo from a JSON string
embedding_info_instance = EmbeddingInfo.from_json(json)
# print the JSON string representation of the object
print(EmbeddingInfo.to_json())

# convert the object into a dict
embedding_info_dict = embedding_info_instance.to_dict()
# create an instance of EmbeddingInfo from a dict
embedding_info_from_dict = EmbeddingInfo.from_dict(embedding_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


