# EmbeddingOptions

Options for embedding generation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**format** | **str** | Output format: html, markdown, json, pdf, plain | [optional] [default to 'html']
**method** | **str** | Embedding method: data-attribute, span, comment | [optional] [default to 'data-attribute']
**include_text** | **bool** | Whether to return text with embeddings | [optional] [default to True]

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


