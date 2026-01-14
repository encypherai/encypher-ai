# ContentMatch

Details of matched content.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_text** | **str** | Matched text segment | 
**segment_hash** | **str** | Hash of the segment | 
**leaf_index** | **int** | Index in Merkle tree | 
**confidence** | **float** | Match confidence (0-1) | 
**source_document_id** | **str** | Source document ID | 
**source_organization_id** | **str** | Source organization ID | 

## Example

```python
from encypher.models.content_match import ContentMatch

# TODO update the JSON string below
json = "{}"
# create an instance of ContentMatch from a JSON string
content_match_instance = ContentMatch.from_json(json)
# print the JSON string representation of the object
print(ContentMatch.to_json())

# convert the object into a dict
content_match_dict = content_match_instance.to_dict()
# create an instance of ContentMatch from a dict
content_match_from_dict = ContentMatch.from_dict(content_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


