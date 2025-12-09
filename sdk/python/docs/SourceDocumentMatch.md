# SourceDocumentMatch

Schema for a source document match in plagiarism report.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** |  | 
**organization_id** | **str** |  | 
**segmentation_level** | **str** |  | 
**matched_segments** | **int** |  | 
**total_leaves** | **int** |  | 
**match_percentage** | **float** |  | 
**confidence_score** | **float** |  | 
**doc_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.source_document_match import SourceDocumentMatch

# TODO update the JSON string below
json = "{}"
# create an instance of SourceDocumentMatch from a JSON string
source_document_match_instance = SourceDocumentMatch.from_json(json)
# print the JSON string representation of the object
print(SourceDocumentMatch.to_json())

# convert the object into a dict
source_document_match_dict = source_document_match_instance.to_dict()
# create an instance of SourceDocumentMatch from a dict
source_document_match_from_dict = SourceDocumentMatch.from_dict(source_document_match_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


