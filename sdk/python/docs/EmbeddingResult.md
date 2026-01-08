# EmbeddingResult

Result for a single embedding found in text.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | Index of this embedding (0-based) | 
**metadata** | **Dict[str, object]** |  | [optional] 
**verification_status** | **str** |  | [optional] [default to 'Not Attempted']
**error** | **str** |  | [optional] 
**verdict** | [**AppRoutersToolsVerifyVerdict**](AppRoutersToolsVerifyVerdict.md) |  | [optional] 
**text_span** | **List[object]** |  | [optional] 
**clean_text** | **str** |  | [optional] 

## Example

```python
from encypher.models.embedding_result import EmbeddingResult

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingResult from a JSON string
embedding_result_instance = EmbeddingResult.from_json(json)
# print the JSON string representation of the object
print(EmbeddingResult.to_json())

# convert the object into a dict
embedding_result_dict = embedding_result_instance.to_dict()
# create an instance of EmbeddingResult from a dict
embedding_result_from_dict = EmbeddingResult.from_dict(embedding_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


