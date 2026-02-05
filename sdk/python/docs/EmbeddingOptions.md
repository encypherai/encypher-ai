# EmbeddingOptions

Options for embedding generation output format.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **str** | Output format: plain, html, markdown, json | [optional] [default to 'plain']
**method** | **str** | Embedding method: invisible (zero-width Unicode), data-attribute, span, comment | [optional] [default to 'invisible']
**include_text** | **bool** | Whether to return text with embeddings in response | [optional] [default to True]

## Example

```python
from encypher.models.embedding_options import EmbeddingOptions

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingOptions from a JSON string
embedding_options_instance = EmbeddingOptions.from_json(json)
# print the JSON string representation of the object
print(EmbeddingOptions.to_json())

# convert the object into a dict
embedding_options_dict = embedding_options_instance.to_dict()
# create an instance of EmbeddingOptions from a dict
embedding_options_from_dict = EmbeddingOptions.from_dict(embedding_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


