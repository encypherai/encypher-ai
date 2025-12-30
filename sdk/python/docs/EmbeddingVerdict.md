# EmbeddingVerdict

Verification verdict for a single embedding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | Index of this embedding (0-based) | 
**valid** | **bool** | Whether the signature is valid | 
**tampered** | **bool** | Whether the payload was tampered | 
**reason_code** | **str** | Reason code describing the verdict | 
**signer_id** | **str** |  | [optional] 
**signer_name** | **str** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 
**text_span** | **List[object]** |  | [optional] 
**clean_text** | **str** |  | [optional] 
**manifest** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.embedding_verdict import EmbeddingVerdict

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingVerdict from a JSON string
embedding_verdict_instance = EmbeddingVerdict.from_json(json)
# print the JSON string representation of the object
print(EmbeddingVerdict.to_json())

# convert the object into a dict
embedding_verdict_dict = embedding_verdict_instance.to_dict()
# create an instance of EmbeddingVerdict from a dict
embedding_verdict_from_dict = EmbeddingVerdict.from_dict(embedding_verdict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


