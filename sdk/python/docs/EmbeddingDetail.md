# EmbeddingDetail

Details for a single detected embedding/signature.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_uuid** | **str** |  |
**leaf_index** | **int** |  | [optional]
**segment_location** | [**SegmentLocationInfo**](SegmentLocationInfo.md) |  | [optional]
**manifest_mode** | **str** |  | [optional]

## Example

```python
from encypher.models.embedding_detail import EmbeddingDetail

# TODO update the JSON string below
json = "{}"
# create an instance of EmbeddingDetail from a JSON string
embedding_detail_instance = EmbeddingDetail.from_json(json)
# print the JSON string representation of the object
print(EmbeddingDetail.to_json())

# convert the object into a dict
embedding_detail_dict = embedding_detail_instance.to_dict()
# create an instance of EmbeddingDetail from a dict
embedding_detail_from_dict = EmbeddingDetail.from_dict(embedding_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
