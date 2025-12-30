# EncodeWithEmbeddingsRequest

Request to encode document with minimal signed embeddings.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Unique document identifier | 
**text** | **str** | Full document text to encode | 
**segmentation_level** | **str** | Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word | [optional] [default to 'sentence']
**action** | **str** | C2PA action type: c2pa.created (new content) or c2pa.edited (modified content) | [optional] [default to 'c2pa.created']
**previous_instance_id** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 
**c2pa_manifest_url** | **str** |  | [optional] 
**c2pa_manifest_hash** | **str** |  | [optional] 
**custom_assertions** | **List[Dict[str, object]]** |  | [optional] 
**template_id** | **str** |  | [optional] 
**validate_assertions** | **bool** | Whether to validate custom assertions against registered schemas | [optional] [default to True]
**digital_source_type** | **str** |  | [optional] 
**license** | [**LicenseInfo**](LicenseInfo.md) |  | [optional] 
**rights** | [**AppSchemasEmbeddingsRightsMetadata**](AppSchemasEmbeddingsRightsMetadata.md) |  | [optional] 
**embedding_options** | [**EmbeddingOptions**](EmbeddingOptions.md) | Embedding generation options | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from encypher.models.encode_with_embeddings_request import EncodeWithEmbeddingsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EncodeWithEmbeddingsRequest from a JSON string
encode_with_embeddings_request_instance = EncodeWithEmbeddingsRequest.from_json(json)
# print the JSON string representation of the object
print(EncodeWithEmbeddingsRequest.to_json())

# convert the object into a dict
encode_with_embeddings_request_dict = encode_with_embeddings_request_instance.to_dict()
# create an instance of EncodeWithEmbeddingsRequest from a dict
encode_with_embeddings_request_from_dict = EncodeWithEmbeddingsRequest.from_dict(encode_with_embeddings_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


