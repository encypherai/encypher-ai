# DocumentEncodeRequest

Request schema for encoding a document into Merkle trees.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Unique identifier for the document | 
**text** | **str** | Document text content to encode | 
**segmentation_levels** | **List[str]** | Segmentation levels to encode (word/sentence/paragraph/section) | [optional] [default to [sentence]]
**include_words** | **bool** | Whether to include word-level segmentation | [optional] [default to False]
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.document_encode_request import DocumentEncodeRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentEncodeRequest from a JSON string
document_encode_request_instance = DocumentEncodeRequest.from_json(json)
# print the JSON string representation of the object
print(DocumentEncodeRequest.to_json())

# convert the object into a dict
document_encode_request_dict = document_encode_request_instance.to_dict()
# create an instance of DocumentEncodeRequest from a dict
document_encode_request_from_dict = DocumentEncodeRequest.from_dict(document_encode_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


