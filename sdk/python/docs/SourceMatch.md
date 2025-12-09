# SourceMatch

Schema for a single source match.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Source document identifier | 
**organization_id** | **str** | Organization that owns the document | 
**root_hash** | **str** | Merkle root hash | 
**segmentation_level** | **str** | Segmentation level | 
**matched_hash** | **str** | Hash that matched | 
**text_content** | **str** |  | [optional] 
**confidence** | **float** | Confidence score (0-1) | 

## Example

```python
from encypher.models.source_match import SourceMatch

# TODO update the JSON string below
json = "{}"
# create an instance of SourceMatch from a JSON string
source_match_instance = SourceMatch.from_json(json)
# print the JSON string representation of the object
print(SourceMatch.to_json())

# convert the object into a dict
source_match_dict = source_match_instance.to_dict()
# create an instance of SourceMatch from a dict
source_match_from_dict = SourceMatch.from_dict(source_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


