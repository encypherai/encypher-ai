# DocumentEncodeResponse

Response schema for document encoding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether encoding was successful | 
**message** | **str** | Success or error message | 
**document_id** | **str** | Document identifier | 
**organization_id** | **str** | Organization identifier | 
**roots** | [**Dict[str, MerkleRootResponse]**](MerkleRootResponse.md) | Dictionary mapping segmentation level to Merkle root | 
**total_segments** | **Dict[str, int]** | Number of segments at each level | 
**processing_time_ms** | **float** | Processing time in milliseconds | 
**fuzzy_index** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.document_encode_response import DocumentEncodeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentEncodeResponse from a JSON string
document_encode_response_instance = DocumentEncodeResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentEncodeResponse.to_json())

# convert the object into a dict
document_encode_response_dict = document_encode_response_instance.to_dict()
# create an instance of DocumentEncodeResponse from a dict
document_encode_response_from_dict = DocumentEncodeResponse.from_dict(document_encode_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


